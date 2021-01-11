if __name__ == "__main__":
    from wand import image
    import os

    count = 0
    for file in os.listdir("ideas/icons"):
        if(file.endswith(".dds")):
            file_name = ".".join(file.split(".")[:-1])
            with image.Image(filename="ideas/icons/" + file) as img:
                img.compression = "no"
                img.save(filename="ideas/icons/" + file_name + ".gif")
                print("Converted files: " + str(count), end="\r")
                count += 1
