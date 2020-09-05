"""image to ascii converter"""
import pathlib
import argparse
import numpy as np

from colour import Color
from PIL import Image, ImageDraw, ImageFont

# cli
parser = argparse.ArgumentParser(
    description="Image to ASCII converter",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("file", type=pathlib.Path, help="path to image to convert")
parser.add_argument(
    "--grayscale-weighting",
    nargs=3,
    default=[0.21, 0.72, 0.07],
    metavar="f",
    help="RGB to Grayscale weighting",
)
parser.add_argument("--scale-factor", default=0.25, help="scale factor", type=float)

# misc useful bits
ascii_chars = np.array(list("#&B9@?sri:,. "))
grayscale = lambda x, w: np.dot(x, w)
normalise = lambda x: (x - x.min()) / np.ptp(x)

if __name__ == "__main__":
    cla = parser.parse_args()
    image = Image.open(cla.file)

    # get the font and determine correction factor based on size
    font = ImageFont.load_default()
    font_size = font.getsize("x")
    correction_factor = np.divide(*font_size[::-1])

    # determine new size and scale original image
    new_size = (
        int(round(image.size[0] * cla.scale_factor * correction_factor)),
        int(round(image.size[1] * cla.scale_factor)),
    )

    # convert image to grayscale and map pixels to ascii characters
    new_image = grayscale(image.resize(new_size), cla.grayscale_weighting)
    ascii_mapping = ((ascii_chars.size - 1) * normalise(new_image)).astype(int)

    # create new file with correct size, and get draw instance to actually write on
    new_file = Image.new("RGBA", tuple(np.multiply(font_size, new_size)), "white")
    draw = ImageDraw.Draw(new_file)
    colour = Color("black")

    # loop over rows in image, and draw it to new image
    for i, line in enumerate(["".join(r) for r in ascii_chars[ascii_mapping]]):
        draw.text((0, i * font_size[1]), line, colour.hex, font=font)

    # save the new file, appending ascii before suffix
    new_filename = cla.file.with_name(cla.file.stem + ".ascii" + cla.file.suffix)
    new_file.save(new_filename)
