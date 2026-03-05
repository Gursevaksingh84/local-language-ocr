
from PIL import Image
img=Image.open("test_image.jpeg")
print("Format:", img.format)
print("Mode:", img.mode)           
print("Size:", img.size)           
print("Width:", img.width)
print("Height:", img.height)
img.show()
resized=img.resize((800,600))
print("New size:", resized.size)
gray = img.convert("L")   # "L" means Luminance = grayscale
gray.show()
print("Grayscale mode:", gray.mode)   # Should print: L

# ── Save the grayscale version ─────────────────────────
gray.save("test_gray.jpg")
print("Saved grayscale image!")
