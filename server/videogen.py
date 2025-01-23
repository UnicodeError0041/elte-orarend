import cv2
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Final
import time
import numpy as np
import random

@dataclass
class Block:
    start_time: int
    end_time: int
    order: int
    start_height: int
    end_height: int
    color: bool

    def __hash__(self):
        return hash(id(self))

@dataclass
class Day:
    blocks: np.ndarray[Block, Block]
    order: int

@dataclass
class Video:
    days: list[Day]
    fps: int


NAMES: Final[list[str]] = [""]# ["Analízis II Ea", "Analízis II Gy", "Programozáselmélet", "Eseményvezérelt Alkalmazások Ea+Gy", "Diszkrét matematika II Ea", "Diszkrét matematika II Gy", "Algoritmusok és Adatszerkezetek II Ea", "Algoritmusok és Adatszerkezetek II Gy", "Webprogramozás Ea+Gy"]
DAYS: Final[list[str]] = ['Hétfő' , 'Kedd' , 'Szerda' , 'Csütörtök' , 'Péntek']
LOCATIONS: Final[list[str]] = [""] #["Bolyai", "Mogyoródi", "Déli Tömb", "Északi Tömb"]
COURSES: Final[list[str]] = ["1", "2", "3", "4", "5", "6", "7"]
TEACHERS: Final[list[str]] = [""] #["Reimu Hakurei", "Marisa Kirisame", "Patchouli Knowledge", "Remilia Scarlet", "Izayoi Sakuya", "Flemish Scarlet", "Konpaku Youmu", "Saigyouji Yuyuko"]

START_HOUR: Final[int] = 8
END_HOUR: Final[int] = 22

BLACK_TYPE: Final[str] = "gyakorlat"
WHITE_TYPE: Final[str] = "előadás"

@dataclass_json
@dataclass
class Lesson:
    name: str
    code: str
    day: str
    time: str
    location: str
    type: str
    course: str
    teacher: str
    comment: str

@dataclass_json
@dataclass
class LessonBlock:
    lesson: Lesson
    order:int
    start_time: int
    end_time: int

@dataclass_json
@dataclass
class LessonVideo:
    blocks: list[LessonBlock]
    fps: int
    frame_count: int


def video_to_boolean_array(video_path: str, output_resolution: tuple[int, int], output_fps:int, threshold:int=128)-> list[list[list[bool]]]:
    # Initialize video capture
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        return []
    
    # Get original FPS and calculate frame skip factor
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_skip = int(original_fps / output_fps)
    print(f"Original FPS: {original_fps}, Frame Skip: {frame_skip}")
    
    # Output list to store boolean frames
    boolean_frames = []
    
    frame_count = 0
    while cap.isOpened():
        # Read a frame
        ret, frame = cap.read()
        
        # Stop if we reached the end of the video
        if not ret:
            print("Reached the end of the video or could not read a frame.")
            break
        
        # Process only frames based on the frame_skip factor
        if frame_count % frame_skip == 0:
            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Resize to output resolution
            resized_frame = cv2.resize(gray_frame, output_resolution)
            
            # Convert to boolean array based on threshold
            boolean_frame = (resized_frame < threshold).astype(np.int32)
            boolean_frames.append(boolean_frame.tolist())
        
        frame_count += 1

    cap.release()
    return boolean_frames

def boolean_array_to_video(arr: list[list[list[bool]]], fps: int, output_resolution: tuple[int, int]) -> Video:
    (block_size, mod) = divmod(output_resolution[0], 5)

    if (mod != 0):
        raise Exception("Nem osztható a kimeneti felbontás 5-tel")
    
    day_blocks: list[list[list[list[Block]]]] = []

    for i in range(5):
        day_blocks.append([])
        for time in range(len(arr)):
            day_blocks[-1].append([])
            for row in range(output_resolution[1]):
                day_blocks[-1][-1].append([])
                for order in range(block_size*i, block_size*(i + 1)):
                    day_blocks[-1][-1][-1].append(Block(time, time, order % block_size, row, row, arr[time][row][order]))
    
    days: list[Day] = []
    for i, blocks_arr in enumerate(day_blocks):
        days.append(Day(np.array(blocks_arr),i))
    
    return Video(days, fps)

def time_compress_video(video: Video):

    def can_merge(block1: Block, block2: Block) -> bool:
        return  block1.start_height == block2.start_height and \
                block1.end_height == block2.end_height and \
                block1.color == block2.color and \
                block1.order == block2.order
                # block1.end_time + 1 == block2.start_time

    for day in video.days:
        # day.blocks.sort(key=lambda block: block.start_time)

        # frame1 = 0
        # while frame1 < day.blocks.shape[0]:

        for frame1, row1, column1 in np.ndindex(day.blocks.shape[0] - 1, day.blocks.shape[1], day.blocks.shape[2]):
            frame2 = frame1 + 1
            # processed = set()

            for column2 in range(day.blocks.shape[2]):

                row2 = row1

                block1 = day.blocks[frame1, row1, column1]
                block2 = day.blocks[frame2, row2, column2]

                if can_merge(block1, block2):
                    block1.end_time = block2.end_time
                    day.blocks[frame2, row2, column2] = block1
                
                # processed.add(block2)

            # frame1 += 1


def horizontal_compress_row(row_blocks: np.ndarray[Block, Block]):
    for block_count in range(1, len(row_blocks) + 1):
        block_len, mod = divmod(len(row_blocks), block_count)

        if (mod != 0):
            continue
        
        success = True

        for i in range(block_count):
            color = row_blocks[i * block_len].color
            
            for j in range(i * block_len + 1, (i + 1) * block_len):
                if row_blocks[j].color != color:
                    success = False
                    break
            
            if not success:
                break
        
        if not success:
            continue

        for i in range(block_count):
            row_blocks[i * block_len].order = i

            for j in range(i * block_len + 1, (i + 1) * block_len):
                row_blocks[j] = row_blocks[i]

        return


def horizontal_compress_video(video: Video):
    # start_time = time.perf_counter()

    for day in video.days:
        # day.blocks.sort(key=lambda block: block.order)
        # blocks_set = set(day.blocks)
        # for frame in range(frame_count):

        #     # progress = (day.order * frame_count + frame) / (frame_count * 5)
        #     # eta = (time.perf_counter() - start_time) / (progress + 0.000001) - (time.perf_counter() - start_time)
        #     # print(f"\t\t Frame {frame} out of {frame_count}, Day {day.order} out of 5, {progress * 100:00f}% complete ETA: {eta}      ", end="\r")

        #     for row in range(day_height):
        #         row_blocks = list(filter(lambda block: block.start_height == row and block.start_time == frame, day.blocks))

        #         horizontal_compress_row(row_blocks, blocks_set)
        #         # day.blocks.sort(key=lambda block: block.order)
        # day.blocks = list(blocks_set)
        for (frame, row) in np.ndindex(day.blocks.shape[0], day.blocks.shape[1]):
            row_blocks = day.blocks[frame, row , :]
            # print(frame, row)
            # raise Exception()
            horizontal_compress_row(row_blocks)

def vertical_compress_video(video: Video):
    # start_time = time.perf_counter()

    for day in video.days:
        for frame in range(day.blocks.shape[0]):
            prev_row_blocks = day.blocks[frame, 0, :].copy()

            for row in range(1, day.blocks.shape[1]):
                row_blocks = day.blocks[frame, row, :]

                row_block_count = len(set(row_blocks))
                prev_row_block_count = len(set(prev_row_blocks))


                if row_block_count != prev_row_block_count:
                    prev_row_blocks = row_blocks.copy()
                    continue

                # row_block_len = len(row_blocks) // (row_blocks[-1].order + 1)
                # prev_row_block_len = len(prev_row_blocks) // (prev_row_blocks[-1].order + 1)

                # if row_block_len == prev_row_block_len * 2:
                #     prev_row_blocks[0].end_height += 1
                #     row_blocks[0:row_block_len] = prev_row_blocks[0:row_block_len]
                
                can_extend = True

                for idx, (block, prev_block) in enumerate(zip(row_blocks, prev_row_blocks)):
                    
                    if can_extend and prev_block.color == block.color and prev_block.order == block.order:
                        prev_block.end_height = row
                        row_blocks[idx] = prev_block
                    else:
                        prev_row_blocks[idx] = row_blocks[idx]
                        can_extend = False










                # for i in range(len(row_blocks) // row_block_len):
        #             prev_block = prev_row_blocks[i * row_block_len]
        #             block = row_blocks[i * row_block_len]

        #             if can_extend and block.color == prev_block.color and block.order == prev_block.order:
        #                 row_blocks[i * row_block_len : (i + 1) * row_block_len] = prev_row_blocks[i * row_block_len : (i + 1) * row_block_len]
        #             else:
        #                 # prev_row_blocks[i * block_len : (i+1) * block_len] = row_blocks[i * block_len : (i+1) * block_len].copy()
        #                 can_extend = False
    
        # for _, block in np.ndenumerate(day.blocks):
        #     if block.end_height < row:
        #         block.end_height = row

        # day.blocks.sort(key=lambda block: block.order)
        # blocks_set = set(day.blocks)
        # for frame in range(frame_count):

        #     progress = (day.order * frame_count + frame) / (frame_count * 5)

        #     eta = (time.perf_counter() - start_time) / (progress + 0.000001) - (time.perf_counter() - start_time)
        #     print(f"\t\t Frame {frame} out of {frame_count}, Day {day.order} out of 5, {progress * 100:00f}% complete ETA: {eta}      ", end="\r")

        #     prev_row_blocks = list(filter(lambda block: block.start_height == 0 and block.start_time == frame, day.blocks))

        #     for row in range(1, day_height):
        #         row_blocks = list(filter(lambda block: block.start_height == row and block.start_time == frame, day.blocks))

        #         if len(row_blocks) != len(prev_row_blocks):
        #             prev_row_blocks = row_blocks
        #             continue
                
        #         prev_col_extended = True

        #         for idx, block in enumerate(prev_row_blocks):
        #             if prev_col_extended and row_blocks[idx].color == block.color:
        #                 block.end_height = row_blocks[idx].end_height
        #                 blocks_set.remove(row_blocks[idx])
        #             else:
        #                 prev_row_blocks[idx] = row_blocks[idx]
        #                 prev_col_extended = False

        # day.blocks = list(blocks_set)


def compress_video(video: Video, day_height: int, frames: int) -> Video:
    print("\n\t Compressing horizontally...")
    # horizontal_compress_video(video, day_height, frames)
    horizontal_compress_video(video)

    print("\n\t Compressing vertically...")
    # vertical_compress_video(video, day_height, frames)
    vertical_compress_video(video)

    print("\n\t Compressing time-atically?...")
    time_compress_video(video)
    return video

def block_to_lesson_block(block: Block, day_order:int, day_height: int) -> LessonBlock:
    name = random.choice(NAMES)
    code = str(block.order)
    day = DAYS[day_order]

    day_height_minutes = (END_HOUR - START_HOUR) * 60
    unit_length_minutes = day_height_minutes // day_height

    start_height_minutes = block.start_height * unit_length_minutes + START_HOUR * 60
    end_height_minutes = (block.end_height + 1) * unit_length_minutes + START_HOUR * 60

    start_height_hour, start_height_minutes = divmod(start_height_minutes, 60)
    end_height_hour, end_height_minutes = divmod(end_height_minutes, 60)

    time = f"{start_height_hour:02d}:{start_height_minutes:02d}-{end_height_hour:02d}:{end_height_minutes:02d}"

    location = random.choice(LOCATIONS)
    type = BLACK_TYPE if block.color else WHITE_TYPE
    course = str(block.order)#random.choice(COURSES)
    teacher = random.choice(TEACHERS)
    comment = teacher

    lesson = Lesson(name, code, day, time, location, type, course, teacher, comment)

    return LessonBlock(lesson, block.order, block.start_time, block.end_time)


def video_to_lesson_video(video: Video, day_height: int) -> LessonVideo:
    lessonBlocks: list[LessonBlock] = []
    for days in video.days:
        for block in set(days.blocks.flatten()):
            lessonBlocks.append(block_to_lesson_block(block, days.order, day_height))
    
    return LessonVideo(lessonBlocks, video.fps, video.days[0].blocks.shape[0])

def main():
    path = input("Path: ")
    res_input = int(input("Resolution: "))
    res = (res_input, res_input) #input("Resolution: ")
    fps = int(input("FPS: "))
    maxFrameCount = int(input("Max frame count: "))

    print("\nReading video into boolean arrays...")
    bool_arr_result = video_to_boolean_array(path, res, fps)[:maxFrameCount]

    print("\nConverting video into blocks...")
    video = boolean_array_to_video(bool_arr_result, fps, res)

    print("\nCompressing video...")
    video = compress_video(video, res[1], len(bool_arr_result))

    print("\nConverting video to VideoLessons...")
    video_lessons = video_to_lesson_video(video, res[1])

    print("\nConverting to json...")
    video_json = video_lessons.to_json()

    print("\nWriting to file...")
    with open("server/result.json", "w") as f:
        f.write(video_json)

    print("done")
    print(f"{res[0] * res[1] * len(bool_arr_result)} total pixels compressed into {len(video_lessons.blocks)} blocks. {(res[0] * res[1] * len(bool_arr_result)) / len(video_lessons.blocks)} times smaller compression")

if __name__ == "__main__":
    main()