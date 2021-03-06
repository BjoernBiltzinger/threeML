import urlparse
import ftplib
import urllib
import os

from threeML.io.progress_bar import progress_bar


def download_file_from_ftp(ftp_url, destination_directory):
    assert ftp_url[-1] != "/", "A URL for a file cannot end in / (received: %s)" % ftp_url

    tokens = ftp_url.split("/")
    server_url = "/".join(tokens[:-1])
    filename = tokens[-1]

    return download_files_from_directory_ftp(server_url, destination_directory, [filename])[0]


def download_files_from_directory_ftp(ftp_url, destination_directory, filenames=None, namefilter=None):
    # Parse url
    tokens = urlparse.urlparse(ftp_url)
    serverAddress = tokens.netloc
    directory = tokens.path

    # if no filename has been specified, connect first to retrieve the list of files to download

    if filenames == None:

        # Connect to server and log in

        ftp = ftplib.FTP(serverAddress, "anonymous", '', '', timeout=60)

        try:

            ftp.login()

        except:
            # Maybe we are already logged in

            try:

                ftp.cwd('/')

            except:

                # nope! don't know what is happening
                raise

        # Move to origin directory

        ftp.cwd(directory)

        # Retrieve list of files

        filenames = []
        ftp.retrlines('NLST', filenames.append)

        # Close connection (will reopen later)

        ftp.close()

    # Download files with progress report

    downloaded_files = []

    with progress_bar(len(filenames)) as p:

        for i, filename in enumerate(filenames):

            if namefilter != None and filename.find(namefilter) < 0:

                p.increase()

                # Filename does not match, do not download it
                continue

            else:

                local_filename = os.path.join(destination_directory, filename)

                urllib.urlretrieve("ftp://%s/%s/%s" % (serverAddress, directory, filename), local_filename)

                urllib.urlcleanup()

                downloaded_files.append(local_filename)

    return downloaded_files
