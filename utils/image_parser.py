import cv2
import numpy as np
import pytesseract

# Using the tesseract installation path of personal device
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(path):
    # Loads and preprocesses the image into grayscale, apply GaussianBlur and binary image
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    return img, thresh


def find_largest_contour(thresh):
    # Finds the largest external contour in the binary image converted 
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest = max(contours, key=cv2.contourArea)
    return largest


def warp_perspective(img, contour):
    # Does a perspective transform to get a top down view of the board
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    
    if len(approx) != 4:
        raise ValueError("Sudoku board not detected properly.")
    
    pts = approx.reshape(4, 2)
    ordered = order_points(pts)
    
    side = max(
        np.linalg.norm(ordered[0] - ordered[1]),
        np.linalg.norm(ordered[1] - ordered[2])
    )

    dst = np.array([
        [0, 0], 
        [side-1, 0], 
        [side-1, side-1], 
        [0, side-1]
        ], dtype="float32")
    
    matrix = cv2.getPerspectiveTransform(ordered, dst)
    return cv2.warpPerspective(img, matrix, (int(side), int(side)))


def order_points(pts):
    # Orders the four points in the correct order
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    return np.array([
        # Top left
        pts[np.argmin(s)],
        # Top right       
        pts[np.argmin(diff)],
        # Bottom right
        pts[np.argmax(s)],
        # Bottom left
        pts[np.argmax(diff)]   
    ], dtype="float32")


def extract_digits(warped):
    # Splits the warped board into 9x9 board and extracts numbers from every cell using the tesseract 
    try:
        cell_size = warped.shape[0] // 9
        grid = []
        for y in range(9):
            row = []
            for x in range(9):
                x1, y1 = x * cell_size, y * cell_size
                cell = warped[y1:y1 + cell_size, x1:x1 + cell_size]
                digit = recognize_digit(cell)
                row.append(digit)
                
            if len(row) != 9:
                raise ValueError(f"Incomplete row at index {y}")
            grid.append(row)
            
        if len(grid) != 9:
            raise ValueError("Extracted grid is not 9x9")
        
        return grid
    except Exception as e:
        raise ValueError(f"Grid extraction failed: {e}")


def recognize_digit(cell):
    # Applies OCR to extract a digit from a sudoku cell
    h, w = cell.shape
    margin = int(np.mean([h, w]) * 0.1)
    roi = cell[margin:h-margin, margin:w-margin]
    _, roi = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(roi, config='--psm 10 digits')
    text = ''.join(filter(str.isdigit, text))
    # If a cell is empty, it returns 0
    return int(text) if text else 0


def image_to_grid(image_path):
    # Full pipeline to convert an image of a sudoku board into a 9x9 grid of integers    
    img, thresh = preprocess_image(image_path)
    contour = find_largest_contour(thresh)
    warped = warp_perspective(img, contour)
    return extract_digits(warped)