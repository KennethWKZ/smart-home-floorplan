import sys
import pymupdf as fitz
doc = fitz.open(sys.argv[1]); page = doc[2]
pix = page.get_pixmap(dpi=400, clip=fitz.Rect(115, 440, 320, 600)); pix.save(sys.argv[2])
