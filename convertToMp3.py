from mutagen.flac import FLAC, Picture
from pydub.utils import mediainfo
from pydub import AudioSegment
from shutil import copyfile
from sys import argv
import tempfile
import os

SOURCE_MUSIC_EXTENSIONS = ['.flac']
FLAC_EXTENSION = '.flac'
OUTPUT_MUSIC_EXTENSION = '.mp3'
FRON_COVER_TYPE = 3

def create_dir_if_not_exists(dirname):
	if (os.path.isdir(dirname)):
		return
	if (os.path.exists(dirname)):
		raise Exception("'" + dirname + "' is a file. Cannot create directory")
	os.mkdir(dirname)

def get_cover_image(file_path):
	song = FLAC(file_path)
	for picture in song.pictures:
		if picture.type == FRON_COVER_TYPE:
			cover_filename = None
			with tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg') as cover_file:
				cover_file.write(picture.data)
				cover_filename = cover_file.name
			return cover_filename
	return None



def walk_music_tree(current_dir, root, output_dir, relative_path):
	print('relative_path: ' + str(relative_path))
	for file in os.scandir(current_dir):
		if file.is_dir():
			new_relative_path = os.path.join(relative_path, file.name)
			create_dir_if_not_exists(os.path.join(root, output_dir, new_relative_path))
			walk_music_tree(os.path.join(current_dir, file.name), root, output_dir, new_relative_path)
		elif file.is_file():
			just_name = os.path.splitext(file.name)[0] # name without extension
			extension = os.path.splitext(file.name)[1].lower()
			if extension in SOURCE_MUSIC_EXTENSIONS:
				new_path = os.path.join(root, output_dir, relative_path, just_name + OUTPUT_MUSIC_EXTENSION)
				if (os.path.exists(new_path)):
					continue
				sound = AudioSegment.from_file(file.path, extension.replace('.', ''))
				cover_image = None
				if extension == FLAC_EXTENSION:
					cover_image = get_cover_image(file.path)
					print('cover_image: ' + cover_image)
				sound.export(new_path, format="mp3", bitrate="256k", tags=mediainfo(file.path).get('TAG', {}), cover=cover_image)
			elif extension == OUTPUT_MUSIC_EXTENSION:
				new_path = os.path.join(root, output_dir, relative_path, file.name)
				if (os.path.exists(new_path)):
					continue
				copyfile(file.path, new_path)


if __name__ == '__main__':
	if (len(argv) < 3):
		print("Error: expected dir name with audio files and name of output dir")
		exit()
	print(argv)
	try:
		create_dir_if_not_exists(argv[2])
		source_dir = os.path.join(os.getcwd(), argv[1])
		walk_music_tree(source_dir, os.getcwd(), argv[2], '')
	except Exception as exception:
		print(exception)
