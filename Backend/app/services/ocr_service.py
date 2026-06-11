import os
import re
import glob
from pathlib import Path

import fitz
import cv2
import numpy as np
import pandas as pd
import easyocr
from pdf2image import convert_from_path

from app.config import settings


GREEN_LOWER = np.array([35, 25, 40])
GREEN_UPPER = np.array([95, 255, 255])

PINK_LOWER = np.array([120, 20, 50])
PINK_UPPER = np.array([179, 255, 255])

MORPH_KERNEL = np.ones((7, 7), np.uint8)


def extract_page_number(filename: str) -> int:
    match = re.search(r"page[_\-\s]?(\d+)", filename.lower())
    return int(match.group(1)) if match else 10**9


def render_page_rotated(doc, page_index: int, dpi: int = 400) -> np.ndarray:
    page = doc.load_page(page_index)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    pix = page.get_pixmap(matrix=matrix, alpha=False)

    image = np.frombuffer(
        pix.samples,
        dtype=np.uint8
    ).reshape(pix.height, pix.width, 3)

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    return cv2.rotate(image, cv2.ROTATE_180)


def crop_largest_colour_region(
    img_bgr: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    skip_top_fraction: float = 0.0
) -> np.ndarray | None:
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        MORPH_KERNEL,
        iterations=2
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)

    if cv2.contourArea(largest) < 2000:
        return None

    x, y, w, h = cv2.boundingRect(largest)

    crop = img_bgr[y:y + h, x:x + w].copy()

    if skip_top_fraction > 0.0:
        crop_mask = mask[y:y + h, x:x + w]
        row_ratio = (crop_mask > 0).sum(axis=1) / crop_mask.shape[1]

        header_end = 0

        for index, ratio in enumerate(row_ratio):
            if ratio > 0.25:
                header_end = index
                break

        header_end = min(
            header_end + int(skip_top_fraction * crop.shape[0]),
            crop.shape[0] - 1
        )

        crop = crop[header_end:, :]

    return crop


def extract_images_from_pdf(
    pdf_path: str,
    green_dir: str,
    pink_dir: str,
    dpi: int = 400,
    poppler_path: str | None = None
):
    os.makedirs(green_dir, exist_ok=True)
    os.makedirs(pink_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    total_pages = doc.page_count

    pdf2img_kwargs = {"dpi": dpi}

    if poppler_path:
        pdf2img_kwargs["poppler_path"] = poppler_path

    green_count = 0
    pink_count = 0

    for page_index in range(total_pages):
        page_number = page_index + 1

        # Green area: course names
        green_image = render_page_rotated(doc, page_index, dpi=dpi)

        green_crop = crop_largest_colour_region(
            green_image,
            GREEN_LOWER,
            GREEN_UPPER,
            skip_top_fraction=0.06
        )

        if green_crop is not None:
            green_path = os.path.join(
                green_dir,
                f"page_{page_number}_green.png"
            )
            cv2.imwrite(green_path, green_crop)
            green_count += 1

        # Pink area: Z-scores
        pages_img = convert_from_path(
            pdf_path,
            first_page=page_number,
            last_page=page_number,
            **pdf2img_kwargs
        )

        pink_image = cv2.cvtColor(
            np.array(pages_img[0]),
            cv2.COLOR_RGB2BGR
        )

        pink_image = cv2.rotate(
            pink_image,
            cv2.ROTATE_90_CLOCKWISE
        )

        pink_crop = crop_largest_colour_region(
            pink_image,
            PINK_LOWER,
            PINK_UPPER
        )

        if pink_crop is not None:
            pink_path = os.path.join(
                pink_dir,
                f"page_{page_number}_pink.png"
            )
            cv2.imwrite(
                pink_path,
                pink_crop,
                [cv2.IMWRITE_PNG_COMPRESSION, 0]
            )
            pink_count += 1

    doc.close()

    return {
        "total_pages": total_pages,
        "green_images": green_count,
        "pink_images": pink_count
    }


def is_all_caps(text: str) -> bool:
    return any(c.isalpha() for c in text) and all(
        c.isupper() for c in text if c.isalpha()
    )


def has_letters(text: str) -> bool:
    return any(c.isalpha() for c in text)


def pair_degrees_and_universities(lines: list[str]) -> list[tuple[str, str]]:
    pairs = []
    current_degree_lines = []
    current_uni_lines = []
    state = None

    for line in lines:
        if not has_letters(line):
            if state == "degree":
                current_degree_lines.append(line)
            elif state == "uni":
                current_uni_lines.append(line)
            continue

        if is_all_caps(line):
            if state == "uni":
                degree = " ".join(current_degree_lines).strip()
                university = " ".join(current_uni_lines).strip()

                if degree and university:
                    pairs.append((degree, university))

                current_degree_lines = [line]
                current_uni_lines = []
                state = "degree"
            else:
                current_degree_lines.append(line)
                state = "degree"
        else:
            if state == "degree":
                current_uni_lines.append(line)
                state = "uni"
            elif state == "uni":
                current_uni_lines.append(line)

    if state == "uni" and current_degree_lines and current_uni_lines:
        degree = " ".join(current_degree_lines).strip()
        university = " ".join(current_uni_lines).strip()

        if degree and university:
            pairs.append((degree, university))

    return pairs


def extract_course_names_to_csv(
    green_dir: str,
    output_csv: str,
    raw_logs_dir: str,
    gpu: bool = False
):
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    os.makedirs(raw_logs_dir, exist_ok=True)

    images = sorted(
        glob.glob(os.path.join(green_dir, "*.png")) +
        glob.glob(os.path.join(green_dir, "*.jpg")),
        key=lambda path: extract_page_number(os.path.basename(path))
    )

    if not images:
        return {
            "course_count": 0,
            "output_csv": output_csv
        }

    reader = easyocr.Reader(["en"], gpu=gpu)

    all_columns = []

    for image_path in images:
        page_number = extract_page_number(os.path.basename(image_path))

        result = reader.readtext(
            image_path,
            detail=1,
            paragraph=False
        )

        lines = [
            entry[1].strip()
            for entry in result
            if entry[1].strip()
        ]

        raw_log = os.path.join(
            raw_logs_dir,
            f"page{page_number}_raw.txt"
        )

        with open(raw_log, "w", encoding="utf-8") as file:
            for index, line in enumerate(lines, 1):
                file.write(f"{index:3d}: {line}\n")

        pairs = pair_degrees_and_universities(lines)

        # keep two blank placeholders like your original code
        all_columns.append(f"_blank_p{page_number}_1")
        all_columns.append(f"_blank_p{page_number}_2")

        for degree, university in pairs:
            all_columns.append(f"{degree} ({university})")

    display_columns = []

    for index, column in enumerate(all_columns):
        if column.startswith("_blank_"):
            display_columns.append(" " * (index + 1))
        else:
            display_columns.append(column)

    dataframe = pd.DataFrame(columns=display_columns)
    dataframe.to_csv(output_csv, index=False, encoding="utf-8-sig")

    return {
        "course_count": len([c for c in display_columns if c.strip()]),
        "output_csv": output_csv
    }


def cx(bbox) -> float:
    return float(sum(point[0] for point in bbox) / 4)


def cy(bbox) -> float:
    return float(sum(point[1] for point in bbox) / 4)


def h(bbox) -> float:
    ys = [point[1] for point in bbox]
    return float(max(ys) - min(ys))


def cluster_positions(values: list[float], tol: float) -> list[float]:
    values = sorted(values)
    clusters = []

    for value in values:
        if not clusters:
            clusters.append([value])
        elif abs(value - np.mean(clusters[-1])) <= tol:
            clusters[-1].append(value)
        else:
            clusters.append([value])

    return [float(np.mean(cluster)) for cluster in clusters]


def nearest_index(centers: list[float], value: float) -> int:
    return int(np.argmin(np.abs(np.array(centers, dtype=float) - value)))


def image_to_grid(image_path: str, reader: easyocr.Reader) -> pd.DataFrame | None:
    results = reader.readtext(
        image_path,
        detail=1,
        paragraph=False
    )

    items = []

    for bbox, text, conf in results:
        text = str(text).strip()

        if not text:
            continue

        items.append({
            "text": text,
            "conf": float(conf),
            "cx": cx(bbox),
            "cy": cy(bbox),
            "h": h(bbox)
        })

    if not items:
        return None

    heights = sorted([item["h"] for item in items])
    median_h = heights[len(heights) // 2]

    row_tol = max(8.0, 0.6 * median_h)
    col_tol = max(10.0, 0.9 * median_h)

    row_centers = cluster_positions(
        [item["cy"] for item in items],
        tol=row_tol
    )

    col_centers = cluster_positions(
        [item["cx"] for item in items],
        tol=col_tol
    )

    grid = [
        ["" for _ in range(len(col_centers))]
        for _ in range(len(row_centers))
    ]

    for item in items:
        row_index = nearest_index(row_centers, item["cy"])
        col_index = nearest_index(col_centers, item["cx"])

        if grid[row_index][col_index] == "":
            grid[row_index][col_index] = item["text"]
        else:
            grid[row_index][col_index] += " " + item["text"]

    return pd.DataFrame(grid)


def extract_zscores_to_csv(
    pink_dir: str,
    per_page_dir: str,
    final_csv: str,
    gpu: bool = False
):
    os.makedirs(per_page_dir, exist_ok=True)
    os.makedirs(os.path.dirname(final_csv), exist_ok=True)

    images = sorted(
        glob.glob(os.path.join(pink_dir, "*.png")) +
        glob.glob(os.path.join(pink_dir, "*.jpg")),
        key=lambda path: extract_page_number(os.path.basename(path))
    )

    if not images:
        return {
            "pages_processed": 0,
            "final_csv": final_csv
        }

    reader = easyocr.Reader(["en"], gpu=gpu)

    all_dataframes = []
    saved_pages = 0

    for image_path in images:
        page_number = extract_page_number(os.path.basename(image_path))

        raw_df = image_to_grid(image_path, reader)

        if raw_df is None:
            continue

        page_csv = os.path.join(
            per_page_dir,
            f"page{page_number}.csv"
        )

        raw_df.to_csv(
            page_csv,
            index=False,
            header=False,
            encoding="utf-8-sig"
        )

        all_dataframes.append(raw_df)
        saved_pages += 1

    if not all_dataframes:
        return {
            "pages_processed": 0,
            "final_csv": final_csv
        }

    frames = [all_dataframes[0]]

    for dataframe in all_dataframes[1:]:
        frames.append(dataframe.iloc[:, 2:])

    merged = pd.concat(
        frames,
        axis=1,
        ignore_index=True
    )

    merged.to_csv(
        final_csv,
        index=False,
        header=False,
        encoding="utf-8-sig"
    )

    return {
        "pages_processed": saved_pages,
        "total_rows": merged.shape[0],
        "total_columns": merged.shape[1],
        "final_csv": final_csv
    }


def course_header_to_degree_university(header: str):
    header = str(header).strip()

    match = re.match(r"^(.*?)\s*\((.*?)\)\s*$", header)

    if not match:
        return header, ""

    degree = match.group(1).strip()
    university = match.group(2).strip()

    return degree, university


def build_extracted_rows_from_csv(
    course_csv: str,
    zscore_csv: str,
    year: str = "2024"
):
    course_df = pd.read_csv(course_csv, encoding="utf-8-sig")

    course_headers = [
        column.strip()
        for column in course_df.columns
        if str(column).strip()
    ]

    zscore_df = pd.read_csv(
        zscore_csv,
        header=None,
        encoding="utf-8-sig"
    )

    extracted_rows = []

    for _, row in zscore_df.iterrows():
        row_values = [str(value).strip() for value in row.tolist()]

        district_name = None

        for value in row_values[:3]:
            if value and not re.match(r"^-?\d+(\.\d+)?$", value) and value.upper() != "NAN":
                district_name = value
                break

        if not district_name:
            continue

        # Remove first two possible district/placeholder columns
        score_values = row_values[2:]

        usable_count = min(len(course_headers), len(score_values))

        for index in range(usable_count):
            score = score_values[index]

            if not score or score.lower() == "nan":
                continue

            degree_name, university_name = course_header_to_degree_university(
                course_headers[index]
            )

            extracted_rows.append({
                "university_name": university_name,
                "program_name": degree_name,
                "district_name": district_name,
                "cutoff_mark": score,
                "year": year
            })

    return extracted_rows


def run_full_ocr_pipeline(
    pdf_path: str,
    job_id: str,
    year: str = "2024"
):
    base_dir = Path(settings.OCR_OUTPUT_DIR) / str(job_id)

    green_dir = str(base_dir / "images" / "green")
    pink_dir = str(base_dir / "images" / "pink")
    output_dir = str(base_dir / "output")
    raw_logs_dir = str(base_dir / "output" / "raw_logs")
    per_page_dir = str(base_dir / "output" / "zscores_per_page")

    course_csv = str(base_dir / "output" / "course_names.csv")
    zscore_csv = str(base_dir / "output" / "zscores_all.csv")

    os.makedirs(output_dir, exist_ok=True)

    image_result = extract_images_from_pdf(
        pdf_path=pdf_path,
        green_dir=green_dir,
        pink_dir=pink_dir,
        dpi=settings.OCR_DPI,
        poppler_path=settings.OCR_POPPLER_PATH or None
    )

    course_result = extract_course_names_to_csv(
        green_dir=green_dir,
        output_csv=course_csv,
        raw_logs_dir=raw_logs_dir,
        gpu=settings.OCR_GPU
    )

    zscore_result = extract_zscores_to_csv(
        pink_dir=pink_dir,
        per_page_dir=per_page_dir,
        final_csv=zscore_csv,
        gpu=settings.OCR_GPU
    )

    extracted_rows = build_extracted_rows_from_csv(
        course_csv=course_csv,
        zscore_csv=zscore_csv,
        year=year
    )

    return {
        "base_dir": str(base_dir),
        "course_csv": course_csv,
        "zscore_csv": zscore_csv,
        "image_result": image_result,
        "course_result": course_result,
        "zscore_result": zscore_result,
        "rows": extracted_rows
    }