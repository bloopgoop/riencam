"""
Implements padding and layout utilities for Rectangles (similar to CSS)
"""

from rectangle import Rectangle


def padding(rect: Rectangle, p=0, top=0, right=0, bottom=0, left=0, x=0, y=0):
    """
    Apply padding to a rectangle, reducing its usable area.
    
    Args:
        rect: The Rectangle to apply padding to
        p: Padding on all sides (default: 0)
        top, right, bottom, left: Individual padding values (override p)
        x: Padding on left and right (overrides p for horizontal)
        y: Padding on top and bottom (overrides p for vertical)
    
    Returns:
        A new Rectangle with padding applied
    """
    # Determine padding values with precedence: specific > x/y > p
    pad_top = top if top > 0 else (y if y > 0 else p)
    pad_right = right if right > 0 else (x if x > 0 else p)
    pad_bottom = bottom if bottom > 0 else (y if y > 0 else p)
    pad_left = left if left > 0 else (x if x > 0 else p)
    
    return Rectangle(
        rect.x + pad_left,
        rect.y + pad_top,
        rect.width - pad_left - pad_right,
        rect.height - pad_top - pad_bottom
    )


def margin(rect: Rectangle, m=0, top=0, right=0, bottom=0, left=0, x=0, y=0):
    """
    Apply margin to a rectangle, expanding its area.
    (Opposite of padding - moves the rectangle outward)
    
    Args:
        rect: The Rectangle to apply margin to
        m: Margin on all sides (default: 0)
        top, right, bottom, left: Individual margin values (override m)
        x: Margin on left and right (overrides m for horizontal)
        y: Margin on top and bottom (overrides m for vertical)
    
    Returns:
        A new Rectangle with margin applied
    """
    # Determine margin values with precedence: specific > x/y > m
    marg_top = top if top > 0 else (y if y > 0 else m)
    marg_right = right if right > 0 else (x if x > 0 else m)
    marg_bottom = bottom if bottom > 0 else (y if y > 0 else m)
    marg_left = left if left > 0 else (x if x > 0 else m)
    
    return Rectangle(
        rect.x - marg_left,
        rect.y - marg_top,
        rect.width + marg_left + marg_right,
        rect.height + marg_top + marg_bottom
    )


def inset(rect: Rectangle, offset=0, top=0, right=0, bottom=0, left=0):
    """
    Create an inset rectangle (shrink from edges).
    
    Args:
        rect: The Rectangle to inset
        offset: Inset on all sides (default: 0)
        top, right, bottom, left: Individual inset values (override offset)
    
    Returns:
        A new inset Rectangle
    """
    ins_top = top if top > 0 else offset
    ins_right = right if right > 0 else offset
    ins_bottom = bottom if bottom > 0 else offset
    ins_left = left if left > 0 else offset
    
    return Rectangle(
        rect.x + ins_left,
        rect.y + ins_top,
        rect.width - ins_left - ins_right,
        rect.height - ins_top - ins_bottom
    )


def center_in(parent: Rectangle, child_width, child_height):
    """
    Center a child rectangle within a parent rectangle.
    
    Args:
        parent: The parent Rectangle
        child_width: Width of the child element
        child_height: Height of the child element
    
    Returns:
        A new Rectangle for the centered child
    """
    child_x = parent.x + (parent.width - child_width) // 2
    child_y = parent.y + (parent.height - child_height) // 2
    
    return Rectangle(child_x, child_y, child_width, child_height)


def align_horizontal(rect: Rectangle, width, align="center"):
    """
    Align content horizontally within a rectangle.
    
    Args:
        rect: The Rectangle to align within
        width: Width of the content
        align: "left", "center", or "right"
    
    Returns:
        The x position of the aligned content
    """
    if align == "left":
        return rect.x
    elif align == "right":
        return rect.x + rect.width - width
    else:  # center
        return rect.x + (rect.width - width) // 2


def align_vertical(rect: Rectangle, height, align="center"):
    """
    Align content vertically within a rectangle.
    
    Args:
        rect: The Rectangle to align within
        height: Height of the content
        align: "top", "center", or "bottom"
    
    Returns:
        The y position of the aligned content
    """
    if align == "top":
        return rect.y
    elif align == "bottom":
        return rect.y + rect.height - height
    else:  # center
        return rect.y + (rect.height - height) // 2