from django.conf import settings
import base64
from openai import OpenAI as OAI
import io


class OpenAI:
    def __init__(self):
        self.model = "gpt-3.5-turbo-1106"
        self.client = OAI(api_key=settings.OPENAI_API_KEY)

    def vision(self, image_content, prefix_question="What’s in this image?"):
        # convert the image content to base64 string
        base64_image = base64.b64encode(image_content).decode("utf-8")

        self.model = 'gpt-4-vision-preview'
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prefix_question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content

    def transcript(self, audio_bytes: bytes) -> str:
        # get audio file from the content
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.ogg"
        audio_file.seek(0)

        transcript = self.client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
        )

        return transcript.text

    def speech(self, content: str, model='tts-1', voice='nova'):
        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=content,
            response_format="mp3",
        )

        return response
