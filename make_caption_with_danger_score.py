import os
import cv2
import json
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

class ImageCaptioningTool:
    def __init__(self, root, image_folder):
        self.root = root
        self.captions = {}
        self.check_vars = {}  # To keep track of checkbox variables
        self.dg_scores = {}
        self.image_folder = image_folder
        self.image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
        self.current_image_index = 0

        self.caption_label = Label(self.root, text="Caption과 위험도를 입력 후 Enter키를 누르면 다음 이미지로 넘어갑니다.")
        self.caption_label.pack(side=TOP, pady=(10, 0))

        self.caption_label = Label(self.root, text="Caption example : A man wearing black shirt is attacking the old man in the hall.")
        self.caption_label.pack(side=TOP, pady=(10, 0))

        self.caption_entry = Entry(self.root, width=100)
        self.caption_entry.pack(side=TOP, pady=(0, 10), padx=20)
        self.caption_entry.bind('<Return>', self.on_enter_key)

        self.dg_score_label = Label(self.root, text="위험도 : 0-1 안전 / 2-4 주의 / 5-7 위험")
        self.dg_score_label.pack(side=TOP, pady=(10, 0))

        self.dg_score_entry = Entry(self.root, width=20)
        self.dg_score_entry.pack(side=TOP, pady=(0, 10), padx=20)
        self.dg_score_entry.bind('<Return>', self.on_enter_key)

        # Create a canvas for scrolling
        self.canvas = Canvas(self.root, borderwidth=0)
        self.canvas.pack(side=RIGHT, fill=BOTH, expand=True)

        self.scrollbar = Scrollbar(self.root, command=self.canvas.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # Populate the frame with image files and associated checkboxes
        for image_file in self.image_files:
            display_name = image_file
            lbl_image = Label(self.frame, text=display_name, anchor='w', width=30)
            lbl_image.grid(row=self.image_files.index(image_file), column=0)
            lbl_image.bind("<Button-1>",
                           lambda event, idx=self.image_files.index(image_file): self.on_image_select(event, idx))

            caption_label = Label(self.frame, text="", width=50, anchor='w')  # Set width to 50 for caption
            caption_label.grid(row=self.image_files.index(image_file), column=1)
            self.captions[image_file] = {"label": caption_label, "text": ""}

            dg_score_label = Label(self.frame, text="", width=10, anchor='w')  # Set width to 10 for danger score
            dg_score_label.grid(row=self.image_files.index(image_file), column=2)
            self.dg_scores[image_file] = 0  # Initialize danger score as 0 for each image

        # GUI Components
        self.image_label = Label(self.root)
        self.image_label.pack(pady=20)

        self.next_button = Button(self.root, text="Next Image", command=self.next_image)
        self.next_button.pack()

        self.prev_button = Button(self.root, text="Previous Image", command=self.prev_image)
        self.prev_button.pack(before=self.next_button)

        self.save_button = Button(self.root, text="Save Captions", command=self.save_captions)
        self.save_button.pack()

        self.format_var = StringVar(self.root)
        self.format_var.set("COCO")  # default value
        self.format_option = OptionMenu(self.root, self.format_var, "COCO", "Flickr")
        self.format_option.pack(pady=10)

        self.load_image()

    def on_image_select(self, event, idx):
        self.current_image_index = idx
        self.load_image()

    def on_enter_key(self, event):
        self.update_caption()
        self.next_image()

    def load_image(self):
        image_path = os.path.join(self.image_folder, self.image_files[self.current_image_index])
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image_pil = Image.fromarray(image).resize((640,480))
        photo = ImageTk.PhotoImage(image_pil)

        self.image_label.config(image=photo)
        self.image_label.image = photo

        # Load saved caption for the image, if exists
        caption = self.captions[self.image_files[self.current_image_index]]["text"]
        self.caption_entry.delete(0, END)  # Clear the entry field
        self.caption_entry.insert(0, caption)  # Insert the saved caption

        # Load saved danger score for the image, if exists
        dg_score = self.dg_scores.get(self.image_files[self.current_image_index], 0)
        self.dg_score_entry.delete(0, END)
        self.dg_score_entry.insert(0, str(dg_score))

    def next_image(self):
        self.update_caption()
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image()
        else:
            print("Reached the end of the image list")

    def prev_image(self):
        self.update_caption()
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image()
        else:
            print("Reached the beginning of the image list")

    def update_caption(self):
        image_name = self.image_files[self.current_image_index]
        caption = self.caption_entry.get()
        display_caption = caption[:50]  # Display only the first 50 characters in the list

        try:
            dg_score = int(self.dg_score_entry.get())
            if dg_score < 0 or dg_score > 7:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Score", "위험도는 0~7 사이의 숫자여야 합니다.")
            return

        if caption.strip():
            self.captions[image_name]["text"] = caption
            self.captions[image_name]["label"].config(text=f"{display_caption}... (위험도: {dg_score})")  # Update the caption label next to the image name with truncated caption
        else:
            self.captions[image_name]["text"] = ""
            self.captions[image_name]["label"].config(text="")  # Clear the caption label

        self.dg_scores[image_name] = dg_score
        # 위험도 출력
        self.captions[image_name]["label"].config(text=f"{caption} (위험도: {dg_score})")

    def save_captions(self):
        self.update_caption()  # Save the caption of the current image

        format_selected = self.format_var.get()
        if format_selected == "COCO":
            self.save_as_coco()
        elif format_selected == "Flickr":
            self.save_as_flickr()

    def save_as_coco(self):
        data = {
            "info": {},
            "images": [],
            "annotations": [],
            "licenses": []
        }

        for idx, image_name in enumerate(self.captions.keys()):
            caption = self.captions[image_name]["text"]
            if not caption.strip():  # Skip if the caption is empty
                continue
            image_info = {
                "id": idx,
                "file_name": image_name
            }
            annotation_info = {
                "image_id": idx,
                "id": idx,
                "caption": caption,
                "danger_score": self.dg_scores.get(image_name, 0)  # 위험도 추가
            }
            data["images"].append(image_info)
            data["annotations"].append(annotation_info)

        with open("captions_coco_format.json", "w") as f:
            json.dump(data, f)

    def save_as_flickr(self):
        data = []

        for image_name in self.captions.keys():
            caption = self.captions[image_name]["text"]
            if not caption.strip():  # Skip if the caption is empty
                continue
            item = {
                "image_name": image_name,
                "caption": caption,
                "danger_score": self.dg_scores.get(image_name, 0)
            }
            data.append(item)

        with open("captions_flickr_format.json", "w") as f:
            json.dump(data, f)


if __name__ == "__main__":
    root = Tk()
    image_folder_path = filedialog.askdirectory(title="Select Image Folder")
    tool = ImageCaptioningTool(root, image_folder_path)
    root.mainloop()
