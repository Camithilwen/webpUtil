from webptools import dwebp, webpmux_extract
from webp import * 
import os
import re
class WEBPconvert:
    '''Contains methods necessary to parse a WEBP file for important header data,
    decompress raw pixel data, and, currently, re-write to a PNG.'''
    def __init__(self):
        self.inData = None
        self.inputPath = None
        
   
    def fileOpen(self, path):
        """Open a binary file
        Returns: 
            - "OK" on success or exception data on reciept."""
        try:
            with open(path, 'rb') as inFile:
                self.inData = inFile.read()
                self.inputPath = path
            return "OK"
        except FileNotFoundError as ex:
            status = str(ex)
            return status
        except Exception as ex:
            status = str(ex)
            return status

    def isAnimated(self):
        """Checks if the given WEBP file is animated.
        Returns:
            - True if animated with more than one animation frame, False otherwise.
            This ensures static "animations" are still converted to PNG."""
        try:
            if self.fileType(self.inData) == "VP8X":
                headerDict = self.parseVP8X()
                if headerDict["animated"]:
                    frameCount = self.getFrameCount()
                    return frameCount > 1
            return False 

        except Exception as ex:
            raise ValueError(f"Error while checking for WEBP animation flag: {ex}")

    def getFrameCount(self):
        """Checks the frame count of an animated WEBP image using 
        wrapped C libraries available through the webp module.

        Returns:
            - Frame count as an integer value."""
        with open(self.inputPath, "rb") as file:
            raw_data = file.read()

        webp_data = ffi.new("struct WebPData *")
        lib.WebPDataInit(webp_data)
        webp_data.bytes = ffi.from_buffer(raw_data)
        webp_data.size = len(raw_data)

        decoder = lib.WebPAnimDecoderNew(webp_data, ffi.NULL)
        if decoder == ffi.NULL:
            raise ValueError("Failed to initialize WebPAnimDecoder.")

        frameCount = 0
        buf_ptr = ffi.new("uint8_t **")
        timestamp_ptr = ffi.new("int *")

        while lib.WebPAnimDecoderGetNext(decoder, buf_ptr, timestamp_ptr):
            frameCount += 1

        return frameCount

    def convertToGif(self, savePath):
        """
        Converts an animated WEBP to GIF using wrapped C libaries available
        through the webp module.
        """
        try:
            # Read WebP data
            with open(self.inputPath, "rb") as file:
                raw_data = file.read()

            # Create a WebPData struct from raw bytes
            webp_data = ffi.new("struct WebPData *")
            lib.WebPDataInit(webp_data)
            webp_data.bytes = ffi.from_buffer(raw_data)
            webp_data.size = len(raw_data)

            # Initialize WebPAnimDecoderOptions
            dec_opts = ffi.new("struct WebPAnimDecoderOptions *")
            dec_opts.color_mode = lib.MODE_RGBA  # Use RGBA color mode
            dec_opts.use_threads = 0  # Disable multithreading

            # Create a decoder object
            decoder = lib.WebPAnimDecoderNew(webp_data, dec_opts)
            if decoder == ffi.NULL:
                raise ValueError("Failed to initialize WebPAnimDecoder.")

            # Initialize and populate WebPAnimInfo
            anim_info = ffi.new("struct WebPAnimInfo *")
            if not lib.WebPAnimDecoderGetInfo(decoder, anim_info):
                raise ValueError("Failed to retrieve animation info.")

            # Initialize frame collection
            frames = []
            durations = []

            # Decode each frame
            buf_ptr = ffi.new("uint8_t **")
            timestamp_ptr = ffi.new("int *")

            while lib.WebPAnimDecoderGetNext(decoder, buf_ptr, timestamp_ptr):
                frame_data = ffi.buffer(buf_ptr[0], anim_info.canvas_width * anim_info.canvas_height * 4)
                frame_image = Image.frombytes("RGBA", (anim_info.canvas_width, anim_info.canvas_height), frame_data)
                frames.append(frame_image)
                durations.append(timestamp_ptr[0] // 10)  # Convert to milliseconds

            # Save frames as a GIF
            if frames:
                frames[0].save(
                    savePath,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    loop=0,
                    duration=durations,
                )

            # Clean up the decoder
            # lib.WebPAnimDecoderDelete(decoder)
            # lib.WebPDataClear(webp_data)
        except Exception as ex:
            raise ValueError(f"Error during GIF conversion: {ex}")


    def fileConvert(self, savePath):
        """Converts the given WEBP file to a PNG or GIF based on the file properties."""
        try:
            if self.isAnimated():
                #Convert animated WEBP to GIF.
                gifPath = f"{os.path.splitext(savePath)[0]}.gif"
                self.convertToGif(gifPath)
                return gifPath
            else:
                #Convert static WEBP to PNG.
                dwebp(input_image=self.inputPath, output_image=f"{savePath}.png", option="-o", logging="-v")
                return f"{savePath}.png"
        except Exception as ex:
            raise ValueError(f"Error during conversion: {ex}")
    
    def fileType(self, header):
        """Checks a provided WEBP file header to determine and return the file's subtype.
        Returns:
            - File subtype of VP8X (extended), VP8L (lossless), or VP8 (lossy)."""
        if re.search(b'^RIFF....WEBPVP8X', header):
            return "VP8X" #extended file type - may contain additional data chunks.
        elif re.search(b'^RIFF....WEBPVP8L', header):
            return "VP8L" #simple lossless
        elif re.search(b'^RIFF....WEBPVP8', header):
            return "VP8" #simple lossy         
        else:
            raise UserWarning("Unknown WEBP subtype.")

    def parseVP8X(self, header=None):
        '''Parses the extended file format for width, height, color space, bitstream encoding, animation presence, and metadata'''
        header = header or self.inData
        vp8xMatch = re.search(b'VP8X(.{7})(.{3})(.{3})', header, re.DOTALL)
        if vp8xMatch:
            #Determine file contents from header bit flags
            flagByte = vp8xMatch.group(1)[0]

            #Check for alpha channel
            alphaBit = bool(flagByte & 0b00010000)

            #Check for ICCP chunk
            ICCPbit = bool(flagByte & 0b00100000)
            colorSpace = "Other (non-sRGB)" if ICCPbit else "sRGB"

            #Check for EXIF and XMP metadata
            EXIFbit = bool(flagByte & 0b00001000)
            XMPbit = bool(flagByte & 0b00000100)

            #Check for animation chunks
            animBit = bool(flagByte & 0b00000010) 
            
            #Determine bitstream compression type
            compressionMatch = re.search(b'VP8X.*(VP8 )', header, re.DOTALL)\
                                or re.search(b'VP8X.*(VP8L)', header, re.DOTALL)
            if compressionMatch.group(1) == b'VP8 ':
                compressionType = "VP8"
            elif compressionMatch.group(1) == b'VP8L':
                compressionType = "VP8L"
            else:
                raise UserWarning("Unknown bitstream compression type.")

            #Determine image width.
            '''1 is added because VP8X width and height information are encoded
            as 24 bit integers with a value of 1 less than true size.
            leading 0 values are stripped from the match result to ensure
            the correct decimalized integer value, but all-0 values are allowed to pass.'''
            widthBytes = vp8xMatch.group(2).lstrip(b'\x00') or b'\x00'
            width = int.from_bytes(widthBytes, byteorder='little') + 1

            #Determine image height.
            heightBytes = vp8xMatch.group(3).lstrip(b'\x00') or b'\x00'
            height = int.from_bytes(heightBytes, byteorder='little') + 1


            #Retrieve EXIF metadata
            '''Chunk size in RIFF containers (such as used by WEBP) is indicated in the
            first four bytes following the four character chunk identifier code.'''
            if EXIFbit:
                EXIFstart = re.search(b'VP8X.*(EXIF)(.{4})', header, re.DOTALL)
                if EXIFstart:
                    EXIFsize = int.from_bytes(EXIFstart.group(2), byteorder='little')
                    EXIFpattern = f'VP8X.*EXIF.{{4}}(.{{{EXIFsize}}})'.encode()
                    EXIFdata = re.search(EXIFpattern, header, re.DOTALL).group(1)
                else: EXIFdata = None
            else:
                EXIFdata = None

            if XMPbit:
                XMPstart = re.search(b'VP8X.*(XMP)(.{4})', header, re.DOTALL)
                if XMPstart:
                    XMPsize = int.from_bytes(XMPstart.group(2), byteorder='little')
                    XMPpattern = f'VP8X.*XMP.{{4}}(.{{{XMPsize}}})'.encode()
                    XMPdata = re.search(XMPpattern, header, re.DOTALL).group(1)
                else:
                    XMPdata = None
            else:
                XMPdata = None
            return {
                "width": width,
                "height": height,
                "alpha": alphaBit,
                "ICC Profile": colorSpace,
                "animated": animBit,
                "compression type": compressionType,
                "EXIF metadata": EXIFdata,
                "XMP metadata": XMPdata
            }
        raise UserWarning("Invalid VP8X subtype.")