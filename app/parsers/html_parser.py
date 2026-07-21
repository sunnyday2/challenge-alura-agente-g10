from bs4 import BeautifulSoup

from app.exceptions import DocumentParseException
from app.parsers.base_parser import AbstractDocumentParser, ExtractedBlock, ExtractionResult


class HtmlParser(AbstractDocumentParser):
    """Extrae texto de HTML eliminando etiquetas, scripts y estilos."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".html", ".htm"]

    def parse(self, content: bytes, filename: str) -> ExtractionResult:
        try:
            soup = BeautifulSoup(content, "lxml")
        except Exception as e:
            raise DocumentParseException(filename, f"No se pudo parsear el HTML: {e}")

        # Eliminar scripts y estilos
        for tag in soup(["script", "style", "head", "meta", "link"]):
            tag.decompose()

        blocks: list[ExtractedBlock] = []
        current_section: str | None = None

        for element in soup.find_all(True):
            tag = element.name

            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                current_section = element.get_text(strip=True)

            elif tag in ("p", "li", "td", "th", "blockquote", "pre"):
                text = element.get_text(separator=" ", strip=True)
                if text:
                    blocks.append(
                        ExtractedBlock(content=text, section_title=current_section)
                    )

        # Fallback: si no encontramos bloques, extraer todo el texto
        if not blocks:
            full_text = soup.get_text(separator="\n", strip=True)
            if full_text:
                blocks.append(ExtractedBlock(content=full_text))

        return ExtractionResult(blocks=blocks)
