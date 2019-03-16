'''
The MIT License (MIT)
Copyright (c) 2014 Patrick Olsen
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
Author: Patrick Olsen
Reference: http://www.decalage.info/python/oletools
Reference: https://github.com/mattgwwalker/msg-extractor
'''
import os, re
import email
import argparse
import olefile


def extractAttachment(msg, eml_files, output_path):
    # print len(msg.get_payload())
    # print msg.get_payload()
    if len(msg.get_payload()) > 2:
        if isinstance(msg.get_payload(), str):
            try:
                extractOLEFormat(eml_files, output_path)
            except IOError:
                # print 'Could not process %s. Try manual extraction.' % (eml_files)
                # print '\tHeader of file: %s\n' % (msg.get_payload()[:8])
                pass

        elif isinstance(msg.get_payload(), list):
            count = 0
            while count < len(msg.get_payload()):
                payload = msg.get_payload()[count]
                filename = payload.get_filename()
                if filename is not None:
                    try:
                        magic = payload.get_payload(decode=True)[:4]
                    except TypeError:
                        magic = "None"
                        # Print the magic deader and the filename for reference.
                    printIT(eml_files, magic, filename)
                    # Write the payload out.
                    writeFile(eml_files, filename, payload, output_path)
                count += 1

    elif len(msg.get_payload()) == 2:
        payload = msg.get_payload()[1]
        filename = payload.get_filename()
        try:
            magic = payload.get_payload(decode=True)[:4]
        except TypeError:
            magic = "None"
        # Print the magic deader and the filename for reference.
        printIT(eml_files, magic, filename)
        # Write the payload out.
        writeFile(eml_files, filename, payload, output_path)

    elif len(msg.get_payload()) == 1:
        attachment = msg.get_payload()[0]
        payload = attachment.get_payload()[1]
        filename = attachment.get_payload()[1].get_filename()
        try:
            magic = payload.get_payload(decode=True)[:4]
        except TypeError:
            magic = "None"
            # Print the magic deader and the filename for reference.
        printIT(eml_files, magic, filename)
        # Write the payload out.
        writeFile(eml_files, filename, payload, output_path)
        # else:
        #    print 'Could not process %s\t%s' % (eml_files, len(msg.get_payload()))


def extractOLEFormat(eml_files, output_path):
    data = '__substg1.0_37010102'
    filename = olefile.OleFileIO(eml_files)
    msg = olefile.OleFileIO(eml_files)
    attachmentDirs = []
    for directories in msg.listdir():
        if directories[0].startswith('__attach') and directories[0] not in attachmentDirs:
            attachmentDirs.append(directories[0])

    for dir in attachmentDirs:
        filename = [dir, data]
        if isinstance(filename, list):
            filenames = "/".join(filename)
            filename = msg.openstream(dir + '/' + '__substg1.0_3707001F').read().replace('\000', '')
            payload = msg.openstream(filenames).read()
            magic = payload[:4]
            # Print the magic deader and the filename for reference.
            printIT(eml_files, magic, filename)
            # Write the payload out.
            writeOLE(filename, payload, output_path)


def printIT(eml_files, magic, filename):
    pass
    # print('Email Name: %s\n\tMagic: %s\n\tSaved File as: %s\n' % (eml_files, magic, filename))


def writeFile(eml_file, filename, payload, output_path):
    try:
        head, tail = os.path.split(eml_file)
        file_location = os.path.join(output_path, tail + '-' + filename)
        open(os.path.join(file_location), 'wb').write(payload.get_payload(decode=True))
    except (TypeError, IOError):
        pass


def writeOLE(filename, payload, output_path):
    open(os.path.join(output_path + filename), 'wb')


def main():
    parser = argparse.ArgumentParser(description='Attempt to parse the attachment from EML messages.')
    parser.add_argument('-p', '--path', help='Path to EML files.')
    parser.add_argument('-o', '--out', help='Path to write attachments to.')
    args = parser.parse_args()

    if args.path:
        input_path = args.path
    else:
        print("You need to specify a path to your EML files.")
        exit(0)

    if args.out:
        output_path = args.out
    else:
        print("You need to specify a path to write your attachments to.")
        exit(0)

    # scan all the eml files in the given path
    for root, subdirs, files in os.walk(input_path):
        for file_names in files:
            eml_files = os.path.join(root, file_names)
            msg = email.message_from_file(open(eml_files))
            extractAttachment(msg, eml_files, output_path)


if __name__ == "__main__":
    main()
