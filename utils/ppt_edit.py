from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import os

from pptx.util import Inches

def insert_image_to_slide(slide, image_path, prs):
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return

    #Get slide dimensions
    slide_width = prs.slide_width
    slide_height = prs.slide_height

    #Set image dimensions
    image_width = Inches(9.5)
    image_height = Inches(3.5)

    #Center the image
    left = (slide_width - image_width) / 2
    top = (slide_height - image_height) / 2

    slide.shapes.add_picture(image_path, left, top, width=image_width, height=image_height)

def update_textbox_with_resource_name(slide, label_prefix, resource_name):
    for shape in slide.shapes:
        if shape.has_text_frame and label_prefix in shape.text:
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = f"{label_prefix} {resource_name}"
            font = run.font
            font.name = "Inter"
            font.size = Pt(48)
            font.bold = True
            p.alignment = PP_ALIGN.LEFT
            return True
    return False


def find_slide_by_title(prs, target_title):
    target_title_lower = target_title.lower().strip()

    for slide_idx, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            try:
                if hasattr(shape, 'text') and shape.text:
                    shape_text = shape.text.lower().strip()
                    if target_title_lower in shape_text or shape_text in target_title_lower:
                        print(f"Found slide with title: '{shape.text}' (slide {slide_idx + 1})")
                        return slide

                if hasattr(shape, 'is_placeholder') and shape.is_placeholder:
                    if shape.placeholder_format.type == 1:
                        if hasattr(shape, 'text') and shape.text:
                            shape_text = shape.text.lower().strip()
                            if target_title_lower in shape_text or shape_text in target_title_lower:
                                print(f"Found slide with title placeholder: '{shape.text}' (slide {slide_idx + 1})")
                                return slide
            except (AttributeError, ValueError):
                continue

    print(f"Could not find slide with title containing: '{target_title}'")
    return None


def find_table_in_slide(slide):
    for shape in slide.shapes:
        if shape.has_table:
            return shape
    return None


def adjust_table_rows(table, data_count):
    current_rows = len(table.rows)
    needed_rows = data_count + 1

    if current_rows < needed_rows:
        rows_to_add = needed_rows - current_rows
        print(f"Adding {rows_to_add} rows to table")
        for _ in range(rows_to_add):
            try:
                last_row = table.rows[-1]._tr
                new_row = last_row.__class__(last_row.xml, last_row)
                table._tbl.append(new_row)
            except Exception as e:
                print(f"Error adding row: {e}")
                break

    elif current_rows > needed_rows >= 1:
        rows_to_remove = current_rows - needed_rows
        max_removable = current_rows - 1
        actual_rows_to_remove = min(rows_to_remove, max_removable)

        if actual_rows_to_remove > 0:
            print(f"Removing {actual_rows_to_remove} empty rows from table")
            try:
                for _ in range(actual_rows_to_remove):
                    if len(table.rows) > 1:
                        row_to_remove = table.rows[-1]._tr
                        table._tbl.remove(row_to_remove)
                    else:
                        break
            except Exception as e:
                print(f"Error removing rows: {e}")


def fill_existing_table(slide, data, keys, slide_title):
    table_shape = find_table_in_slide(slide)

    if not table_shape:
        print(f"No table found in slide '{slide_title}'")
        return False

    table = table_shape.table
    print(f"Found existing table with {len(table.rows)} rows and {len(table.columns)} columns")

    if not data:
        print(f"No data available for '{slide_title}', keeping header only")
        try:
            while len(table.rows) > 1:
                row_to_remove = table.rows[-1]._tr
                table._tbl.remove(row_to_remove)

            if len(table.rows) == 1:
                last_row = table.rows[-1]._tr
                new_row = last_row.__class__(last_row.xml, last_row)
                table._tbl.append(new_row)

            for col_idx in range(min(len(table.columns), len(keys))):
                cell = table.cell(1, col_idx)
                cell.text = "No data available" if col_idx == 0 else ""
        except Exception as e:
            print(f"Error clearing table: {e}")
        return True

    try:
        adjust_table_rows(table, len(data))
    except Exception as e:
        print(f"Error adjusting table rows: {e}")

    if len(table.columns) < len(keys):
        print(f"Warning: Table has {len(table.columns)} columns but need {len(keys)}")
        keys = keys[:len(table.columns)]

    for row_idx, item in enumerate(data, start=1):
        if row_idx >= len(table.rows):
            print(f"Warning: Not enough rows in table for all data (need {len(data) + 1}, have {len(table.rows)})")
            break

        for col_idx, key in enumerate(keys):
            if col_idx >= len(table.columns):
                break

            try:
                text = str(item.get(key, "N/A"))
                cell = table.cell(row_idx, col_idx)
                cell.text = text

                para = cell.text_frame.paragraphs[0]
                para.font.size = Pt(11)
                para.alignment = PP_ALIGN.CENTER

                if row_idx % 2 == 0:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(240, 240, 240)
            except Exception as e:
                print(f"Error filling cell [{row_idx}, {col_idx}]: {e}")

    print(f"Successfully filled table in '{slide_title}' with {len(data)} data rows")
    return True
