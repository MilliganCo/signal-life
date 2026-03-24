from reportlab.lib.pagesizes import inch  # Use inches
from reportlab.pdfgen import canvas


def cmyk_to_rgb(c, m, y, k):
    """
    Convert CMYK to RGB.
    CMYK values are in the range 0-100.
    RGB values are in the range 0-255.
    """
    r = 255 * (1 - c / 100) * (1 - k / 100)
    g = 255 * (1 - m / 100) * (1 - k / 100)
    b = 255 * (1 - y / 100) * (1 - k / 100)
    return int(r), int(g), int(b)


def create_pdf(filename):
    # Create a PDF canvas
    c = canvas.Canvas(filename, pagesize=(40 * inch, 40 * inch))  # Set the page size to inches

    # First set of CMYK values to start with
    cmyk_1 = [30, 40, 40, 15]
    cmyk_2 = [10, 15, 20, 0]

    # Square size and margin in inches
    square_size = 0.787402  # 2 cm in inches
    margin = 0.393701  # 1 cm in inches

    # Helper function to draw squares with changing CMYK values
    def draw_cmyk_squares(cmyk, start_x, start_y):
        for i in range(8):  # Maximum 8 steps (CMYK values change)
            for j in range(8):  # Maximum 8 steps (CMYK values change)
                # Convert CMYK to RGB
                rgb = cmyk_to_rgb(cmyk[0], cmyk[1], cmyk[2], cmyk[3])
                c.setFillColorRGB(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
                c.rect(start_x + j * (square_size + margin), start_y - i * (square_size + margin),
                       square_size, square_size, fill=True)
                # Increment CMYK values
                cmyk = [min(cmyk[0] + 5, 100), min(cmyk[1] + 5, 100), min(cmyk[2] + 5, 100), min(cmyk[3] + 5, 100)]

    # Draw squares for the first CMYK set
    draw_cmyk_squares(cmyk_1, 0, 40 * inch)

    # Draw squares for the second CMYK set
    draw_cmyk_squares(cmyk_2, 0, 20 * inch)

    # Save the canvas to a file
    c.save()


# Generate the PDF file
pdf_path = "colored_squares.pdf"
create_pdf(pdf_path)
