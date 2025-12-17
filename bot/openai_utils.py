import config
import logging
import json

import tiktoken
import openai


# setup openai
openai.api_key = config.openai_api_key
if config.openai_api_base is not None:
    openai.api_base = config.openai_api_base
logger = logging.getLogger(__name__)


def _format_messages_for_log(messages):
    try:
        return json.dumps(messages, ensure_ascii=False)
    except Exception:
        return str(messages)


def _build_completion_options(temperature_override):
    options = dict(config.openai_completion_options)
    if temperature_override is not None:
        options["temperature"] = temperature_override
    return options


class ChatGPT:
    def __init__(self, model="gpt-5-mini"):
        assert model in {"gpt-5-mini",
                         "gpt-5.1",
                         "gpt-5.2"}, f"Unknown model: {model}"
        self.model = model

    async def send_message(self, message, dialog_messages=[], chat_mode="assistant", temperature=None):
        if chat_mode not in config.chat_modes.keys():
            raise ValueError(f"Chat mode {chat_mode} is not supported")

        n_dialog_messages_before = len(dialog_messages)
        answer = None
        while answer is None:
            try:
                if self.model in {"gpt-5-mini",
                                  "gpt-5.1",
                                  "gpt-5.2"}:
                    messages = self._generate_prompt_messages(message, dialog_messages, chat_mode)

                    completion_options = _build_completion_options(temperature)

                    if config.log_openai_requests:
                        logger.info(
                            "OpenAI request | mode=sync | model=%s | messages=%s",
                            self.model,
                            _format_messages_for_log(messages),
                        )

                    r = await openai.ChatCompletion.acreate(
                        model=self.model,
                        messages=messages,
                        **completion_options
                    )
                    answer = r.choices[0].message["content"]
                else:
                    raise ValueError(f"Unknown model: {self.model}")

                answer = self._postprocess_answer(answer)
                n_input_tokens, n_output_tokens = r.usage.prompt_tokens, r.usage.completion_tokens
            except openai.error.InvalidRequestError as e:  # too many tokens
                if len(dialog_messages) == 0:
                    raise ValueError("Dialog messages is reduced to zero, but still has too many tokens to make completion") from e

                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]

        n_first_dialog_messages_removed = n_dialog_messages_before - len(dialog_messages)

        if config.log_openai_responses:
            logger.info(
                "OpenAI response | mode=sync | model=%s | tokens_in=%s | tokens_out=%s | text=%s",
                self.model,
                n_input_tokens,
                n_output_tokens,
                answer,
            )

        return answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

    async def send_message_stream(self, message, dialog_messages=[], chat_mode="assistant", temperature=None):
        if chat_mode not in config.chat_modes.keys():
            raise ValueError(f"Chat mode {chat_mode} is not supported")

        n_dialog_messages_before = len(dialog_messages)
        answer = None
        while answer is None:
            try:
                if self.model in {"gpt-5-mini",
                                  "gpt-5.1",
                                  "gpt-5.2"}:
                    messages = self._generate_prompt_messages(message, dialog_messages, chat_mode)

                    completion_options = _build_completion_options(temperature)

                    if config.log_openai_requests:
                        logger.info(
                            "OpenAI request | mode=stream | model=%s | messages=%s",
                            self.model,
                            _format_messages_for_log(messages),
                        )

                    r_gen = await openai.ChatCompletion.acreate(
                        model=self.model,
                        messages=messages,
                        stream=True,
                        **completion_options
                    )

                    answer = ""
                    async for r_item in r_gen:
                        delta = r_item.choices[0].delta

                        if "content" in delta:
                            answer += delta.content
                            n_input_tokens, n_output_tokens = self._count_tokens_from_messages(messages, answer, model=self.model)
                            n_first_dialog_messages_removed = 0

                            yield "not_finished", answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed

                answer = self._postprocess_answer(answer)

            except openai.error.InvalidRequestError as e:  # too many tokens
                if len(dialog_messages) == 0:
                    raise e

                # forget first message in dialog_messages
                dialog_messages = dialog_messages[1:]

        yield "finished", answer, (n_input_tokens, n_output_tokens), n_first_dialog_messages_removed  # sending final answer
        if config.log_openai_responses:
            logger.info(
                "OpenAI response | mode=stream | model=%s | tokens_in=%s | tokens_out=%s | text=%s",
                self.model,
                n_input_tokens,
                n_output_tokens,
                answer,
            )

    def _generate_prompt(self, message, dialog_messages, chat_mode):
        prompt = config.chat_modes[chat_mode]["prompt_start"]
        prompt += "\n\n"

        # add chat context
        if len(dialog_messages) > 0:
            prompt += "Chat:\n"
            for dialog_message in dialog_messages:
                prompt += f"User: {dialog_message['user']}\n"
                prompt += f"Assistant: {dialog_message['bot']}\n"

        # current message
        prompt += f"User: {message}\n"
        prompt += "Assistant: "

        return prompt

    def _generate_prompt_messages(self, message, dialog_messages, chat_mode):
        prompt = config.chat_modes[chat_mode]["prompt_start"]

        messages = [{"role": "system", "content": prompt}]

        for dialog_message in dialog_messages:
            user_content = dialog_message["user"]
            if isinstance(user_content, list):
                text_chunks = []
                for part in user_content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_chunks.append(part.get("text", ""))
                user_content = "\n".join(chunk for chunk in text_chunks if chunk).strip()
            if not user_content:
                user_content = "[non-text input removed]"
            messages.append({"role": "user", "content": user_content})
            messages.append({"role": "assistant", "content": dialog_message["bot"]})

        messages.append({"role": "user", "content": message})

        return messages

    def _postprocess_answer(self, answer):
        answer = answer.strip()
        return answer

    def _count_tokens_from_messages(self, messages, answer, model="gpt-5-mini"):
        # encoding = tiktoken.encoding_for_model(model)
        encoding = tiktoken.get_encoding("o200k_base")

        if model in {"gpt-5-mini",
                     "gpt-5.1",
                     "gpt-5.2"}:
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise ValueError(f"Unknown model: {model}")

        # input
        n_input_tokens = 0
        for message in messages:
            n_input_tokens += tokens_per_message
            if isinstance(message["content"], list):
                for sub_message in message["content"]:
                    if "type" in sub_message:
                        if sub_message["type"] == "text":
                            n_input_tokens += len(encoding.encode(sub_message["text"]))
                        elif sub_message["type"] == "image_url":
                            pass
            else:
                if "type" in message:
                    if message["type"] == "text":
                        n_input_tokens += len(encoding.encode(message["text"]))
                    elif message["type"] == "image_url":
                        pass


        n_input_tokens += 2

        # output
        n_output_tokens = 1 + len(encoding.encode(answer))

        return n_input_tokens, n_output_tokens

    def _count_tokens_from_prompt(self, prompt, answer, model="gpt-5-mini"):
        # encoding = tiktoken.encoding_for_model(model)
        encoding = tiktoken.get_encoding("o200k_base")

        n_input_tokens = len(encoding.encode(prompt)) + 1
        n_output_tokens = len(encoding.encode(answer))

        return n_input_tokens, n_output_tokens


async def transcribe_audio(audio_file) -> str:
    r = await openai.Audio.atranscribe("whisper-1", audio_file)
    return r["text"] or ""


async def generate_images(prompt, n_images=4, size="512x512"):
    r = await openai.Image.acreate(prompt=prompt, n=n_images, size=size)
    image_urls = [item.url for item in r.data]
    return image_urls


async def is_content_acceptable(prompt):
    r = await openai.Moderation.acreate(input=prompt)
    return not all(r.results[0].categories.values())
