from utils.image_parser import image_to_grid

if __name__ == "__main__":
    path = "samples/test1.jpg"  
    grid = image_to_grid(path)
    for row in grid:
        print(row)
