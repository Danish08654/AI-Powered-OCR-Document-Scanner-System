import os


def allowed_file(filename):

    allowed_extensions = [
        "png",
        "jpg",
        "jpeg"
    ]

    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in allowed_extensions


def create_upload_folder(path="uploads"):

    if not os.path.exists(path):
        os.makedirs(path)

    return path