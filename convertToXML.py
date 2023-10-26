import xml.etree.ElementTree as ET

import os

import re

from datetime import datetime, timedelta


def findAndMoveImage(imagesfolder, old_measurement_id, new_measurement_id, barcode):
    # find the image file name
    # get the first 3 digits of the old_measurement_id
    # for example: 60270 to 602
    old_measurement_id_first_3_digits = old_measurement_id[:3]

    # This 3 digits is the subfolder name
    # for example: 602 to 602
    # subfolder_name = old_measurement_id_first_3_digits
    subfolder_name = os.path.join(imagesfolder, "images", old_measurement_id_first_3_digits)

    # Get the images in the subfolder
    # The image name should be like old_measurement_id + _ + barcode + _ + .jpeg
    # for example: 60270_1234567890123_.jpeg

    # Loop through all .jpeg files in the subfolder
    for filename in os.listdir(subfolder_name):
        if filename.endswith('.jpeg'):
            # Check if the image name contains the old_measurement_id and barcode
            if old_measurement_id in filename and barcode in filename:
                # Move the image to the new subfolder
                # The new subfolder name is the first 3 digits of the new_measurement_id
                # for example: 60271 to 602
                new_subfolder_name = os.path.join(imagesfolder, "images_new", new_measurement_id[:3])

                # Create the new subfolder if it doesn't exist
                if not os.path.exists(new_subfolder_name):
                    os.makedirs(new_subfolder_name)

                # Create the new image file name
                # for example: 60271_1234567890123_.jpeg
                filename_new = new_measurement_id + "_" + barcode + "_.jpeg"

                # Move the image to the new subfolder
                os.rename(subfolder_name + "/" + filename, new_subfolder_name + "/" + filename_new)

                # Break the loop
                break


# Define a function to calculate the new time and date
def calculate_new_time_and_date(time_string, date_string, time_diff_in_sec):
    # Merge the time and date strings
    time_and_date_string = date_string + " " + time_string

    # Convert the time and date string to a datetime object
    time_and_date = datetime.strptime(time_and_date_string, '%Y-%m-%d %H:%M:%S')

    # Add the time difference to the datetime object
    new_time_and_date = time_and_date + timedelta(seconds=time_diff_in_sec)

    # Split the new time and date into separate strings
    # should be in the format Date="26.12.2021" Time="14:09:11"
    new_time_string = new_time_and_date.strftime("%H:%M:%S")
    new_date_string = new_time_and_date.strftime("%d.%m.%Y")

    return new_time_string, new_date_string

# Define the input and output file paths
input_file_path = "input.txt"
output_file_path = "output.xml"

directory_path = 'logs'  # Change this to the directory containing your .txt files

# Initialize the root element
root = ET.Element("Measurements")
root.set("DeviceSerialNumber", "182019")
root.set("DeviceModel", "BeeVision 182")

firstMeasurementID = 60270

# time format is HH:MM:SS
timeString = "13:45:24"

# date format is is YYYY-MM-DD
dateString = "2023-10-19"

# timestamd in second
timestamp = 83334

# Create Page element
page = ET.SubElement(root, "Page")

# Loop through all .txt files in the directory
for filename in os.listdir(directory_path):
    # exclue the filtered.txt, black_objects.txt and non_black_objects.txt files
    if filename.endswith('.txt'):
        
        filename = os.path.join(directory_path, filename)

        print(f"Processing file '{filename}'...")

        # Read data from the input text file and process each line
        with open(filename, "r") as input_file:
            for line in input_file:
                if "MeasurementID:" in line:
                    

                    timeStampString = line.split("0000")[1].split(".")[0]
                    # convert timeStampString to int
                    # for example: 00242 to 242
                    timeStampInt = int(timeStampString)

                    timeDiff = timeStampInt - timestamp

                    # add this time diff to timeString and dateString to get the new time and date

                    new_time_string, new_date_string = calculate_new_time_and_date(timeString, dateString, timeDiff)

                    
                    

                    # print(line)    
                    MeasurementID = line.split("MeasurementID:")[1].split("\n")[0]
                    Barcode = line.split("Barcode:")[1].split(", MeasurementID:")[0]
                    Weight = line.split("Weight=")[1].split(", Barcode:")[0]
                    Height = line.split("Height=")[1].split(", Weight=")[0]
                    Length = line.split("Length=")[1].split(", Height=")[0]
                    Width = line.split("Width=")[1].split(", Length=")[0]


                    # RealVolume = width * height * length * 0.92
                    RealVolume = float(Width) * float(Height) * float(Length) * 0.92

                    # convert RealVolume to int
                    RealVolume = int(RealVolume)

                    # DimWt = (width * height * length) / 5000 rounded up to the nearest 0.25 kg
                    DimWt = (float(Width) * float(Height) * float(Length)) / 5000
                    # round up to the nearest 0.25 kg
                    DimWt = round(DimWt * 4) / 4
                    DimWt = str(DimWt)

                    # print(data)

                    if(int(MeasurementID) > 60090):
                        print(MeasurementID)
                        # Create Measurement element
                        measurement = ET.SubElement(page, "Measurement")
                        measurement.set("Barcode", Barcode)
                        measurement.set("BarcodeType", "")
                        measurement.set("Date", new_date_string)
                        measurement.set("Time", new_time_string)
                        measurement.set("Width", Width)
                        measurement.set("Length", Length)
                        measurement.set("Height", Height)
                        measurement.set("RealVolume", str(RealVolume))
                        measurement.set("Weight", Weight)
                        measurement.set("DimWt", DimWt)
                        measurement.set("MeasurementUnit", "cm")
                        measurement.set("WeightUnit", "kg")
                        measurement.set("BranchID", "6")
                        measurement.set("DeviceID", "")
                        # firstMeasurementID and increment it by 1 for each measurement
                        # measurement.set("MeasurementUID", firstMeasurementID++)
                        firstMeasurementID += 1
                        # convert firstMeasurementID to string
                        firstMeasurementID_str = str(firstMeasurementID)
                        measurement.set("MeasurementUID", firstMeasurementID_str)
                        measurement.set("BarcodeSource", "Manual")
                        measurement.set("DataShared", "0")
                        measurement.set("BatchName", "")
                        measurement.set("IsRegular", "0")
                        measurement.set("OperatorUserId", "admin")
                        measurement.set("Crc", "11111")

                        findAndMoveImage("logs", MeasurementID, firstMeasurementID_str, Barcode)


            




# Create and save the XML file
tree = ET.ElementTree(root)
tree.write(output_file_path)

print(f"XML file '{output_file_path}' created successfully.")
