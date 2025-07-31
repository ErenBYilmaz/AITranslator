import argparse
import whisper
from easynmt import EasyNMT
from kokoro import KPipeline
import soundfile as sf


def transcribe(audio_file: str, model_name: str = "base") -> str:
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_file)
    return result.get("text", "")


def translate_text(text: str, target_lang: str, model_name: str = "opus-mt") -> str:
    translator = EasyNMT(model_name)
    return translator.translate(text, target_lang=target_lang)


def text_to_speech(text: str, lang_code: str = "a", voice: str = "af_heart") -> None:
    pipeline = KPipeline(lang_code=lang_code)
    generator = pipeline(text, voice=voice)
    for i, (_, _, audio) in enumerate(generator):
        sf.write(f"output_{i}.wav", audio, 24000)


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe, translate and speak audio")
    parser.add_argument("audio", help="Path to an audio file")
    parser.add_argument("target_lang", help="Target language code for translation")
    parser.add_argument("--whisper-model", default="base", dest="whisper_model", help="Whisper model to use")
    parser.add_argument("--easynmt-model", default="opus-mt", dest="easynmt_model", help="EasyNMT model to use")
    parser.add_argument("--tts-lang", default="a", dest="tts_lang", help="Kokoro language code")
    parser.add_argument("--voice", default="af_heart", help="Voice name for Kokoro")
    args = parser.parse_args()

    text = transcribe(args.audio, args.whisper_model)
    translated = translate_text(text, args.target_lang, args.easynmt_model)
    print(translated)
    text_to_speech(translated, args.tts_lang, args.voice)


if __name__ == "__main__":
    main()
