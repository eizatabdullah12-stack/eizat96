from pathlib import Path
import sys
from glossary import EngineeringTranslator

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))

class OfflineTranslator(EngineeringTranslator):
    def __init__(self, language):
        import ctranslate2
        import sentencepiece
        base = ROOT / 'models' / language
        sp_files = list(base.rglob('sentencepiece.model'))
        model_files = list(base.rglob('model.bin'))
        if len(sp_files) != 1 or len(model_files) != 1:
            raise RuntimeError('Bundled translation model is incomplete or unsupported. Download a fresh copy of the application.')
        self.sp = sentencepiece.SentencePieceProcessor(model_file=str(sp_files[0]))
        self.engine = ctranslate2.Translator(str(model_files[0].parent), device='cpu', compute_type='int8')
        super().__init__(language, self._model_translate)

    def _model_translate(self, text):
        left, right = text[:len(text)-len(text.lstrip())], text[len(text.rstrip()):]
        pieces = self.sp.encode(text.strip(), out_type=str)
        if not pieces:
            return text
        # Engineering labels are usually short. Chunk longer runs to keep input
        # within the model's training length; sentence context may be reduced.
        batches = [pieces[i:i+120] for i in range(0,len(pieces),120)]
        results = self.engine.translate_batch(batches, beam_size=4, max_decoding_length=300)
        # Argos models can return a literal SentencePiece space marker after
        # decode_pieces; normalize it as the publisher's tokenizer does.
        rendered = ' '.join(self.sp.decode_pieces(r.hypotheses[0]).replace('\u2581', ' ').replace('_', ' ').strip() for r in results)
        return left + rendered + right
