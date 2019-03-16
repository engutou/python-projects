#! python

import email
import extract_msg
from extract_eml import extractAttachment
import os

input_path = './data'
for root, subdirs, files in os.walk(input_path):
    for file_name in files:
        full_file_name = os.path.join(root, file_name)
        if file_name.endswith('.msg'):
            msg = extract_msg.Message(full_file_name)
            for attachment in msg.attachments:
                attachment.save(customPath=root, customFilename=file_name + '-' + attachment.longFilename)

        elif file_name.endswith('.eml'):
            msg = email.message_from_file(open(full_file_name))
            extractAttachment(msg, full_file_name, output_path=root)

        else:
            print('Unknown format, ignore file {0}'.format(full_file_name))

