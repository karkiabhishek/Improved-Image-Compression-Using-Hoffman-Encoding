import heapq
import os
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import numpy as np
from PIL import Image
import ast
from math import ceil
class HeapNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __cmp__(self, other):
        if(other == None):
            return -1
        if(not isinstance(other, HeapNode)):
            return -1
        return self.freq < other.freq
    def __lt__(self, other):
        if(self.freq < other.freq):
            return True
        else:
            return False
    
        


class HuffmanCoding:
    def __init__(self):
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}
        self.imshape=None

    @property
    def colors(self):
        return len(self.reverse_mapping)
    # functions for compression:

    def make_frequency_dict(self, imagearr):
        frequency = {}
        for pixel in imagearr:
            if not pixel in frequency:
                frequency[pixel] = 0
            frequency[pixel] += 1
            
        
        return frequency

    def make_heap(self, frequency):
        for key in frequency:
            node = HeapNode(key, frequency[key])
            heapq.heappush(self.heap, node)

    def merge_nodes(self):
        while(len(self.heap)>1):
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)

            merged = HeapNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2

            heapq.heappush(self.heap, merged)


    def make_codes_helper(self, root, current_code):
        if(root == None):
            return

        if(root.char != None):
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return

        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self):
        root = heapq.heappop(self.heap)
        current_code = ""
        self.make_codes_helper(root, current_code)


    def get_encoded_text(self, imagearr,fun):
        encoded_text = ""
        i=0
        size = len(imagearr)
        for pixel in imagearr:
            encoded_text += self.codes[pixel]
            i+=1
            fun.updateProgress(int(60+35*i/size))
        return encoded_text


    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        encoded_text += '0'*extra_padding

        padded_info = bin(extra_padding)[2:].rjust(8,'0')
        encoded_text = padded_info + encoded_text
        return encoded_text


    def get_byte_array(self, padded_encoded_text):
        if(len(padded_encoded_text) % 8 != 0):
            print("Encoded imagearr not padded properly")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b
    
    def get_bytes_to_write(self,fun):
        b=bytearray()
        size = len(self.reverse_mapping)
        t=bin(self.imshape[0])[2:].rjust(16,'0')+bin(self.imshape[1])[2:].rjust(16,'0')
        for i in range(4):
            b.append(int(t[:8],2))
            t=t[8:]
        ii=0
        for t,tv in self.reverse_mapping.items():
            ii+=1
            l=len(t)
            ll=ceil(l/8)
            t=t.rjust(ll*8,'0')
            b.append(l)
            for i in range(ll):
                b.append(int(t[:8],2))
                t=t[8:]
            fun.updateProgress(int(95+ii*30/size)) 
            fun.refresh()
               
            b.append(tv[0])
            b.append(tv[1])
            b.append(tv[2])
        b.append(0)
        return b

    def compress(self,path,fun):
        filename = os.path.splitext(path)[0]
        output_path = filename + ".bin"
        fun.refresh()
        with open(output_path, 'wb') as output:
            
            image = mpimg.imread(path)
            self.imshape=image.shape
            plt.imshow(image)
            plt.show()
            imagearr=[]
            i=0
            size = self.imshape[0]*self.imshape[1]
            for row in image:
                for pixel in row:
                    i+=1
                    s=tuple(pixel)
                    imagearr.append(s)
                    fun.updateProgress(int(60*i/size))
                    
            frequency = self.make_frequency_dict(imagearr)
            self.make_heap(frequency)
            
            self.merge_nodes()
            fun.refresh()
            self.make_codes()

            print('Colors:',self.colors)
            encoded_text = self.get_encoded_text(imagearr,fun)
            
            padded_encoded_text = self.pad_encoded_text(encoded_text)
            
            output.write(self.get_bytes_to_write(fun))
            b = self.get_byte_array(padded_encoded_text)
            
            output.write(bytes(b))
        print("Compressed")
        fun.label.setText("Image Compressed Successfully!")
        return output_path


    """ functions for decompression: """

    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)

        padded_encoded_text = padded_encoded_text[8:] 
        encoded_text = padded_encoded_text[:-1*extra_padding]

        return encoded_text

    def decode_image(self, encoded_text,fun):
        current_code = ""
        decoded_image = []
        self.count=0
        s=[{} for i in range(30)]
        for k, v in self.reverse_mapping.items():
            ll=len(k)
            s[ll].update({k:v})  
        ss={i for i in range(30) if len(s[i])>0}
        codelen=0
        for bit in encoded_text:
            current_code += bit
            codelen+=1
            if codelen not in ss: continue
            try:
                if(s[codelen].get(current_code)):
                    pixel = s[codelen].get(current_code)
                    decoded_image.append(list(pixel))
                    current_code = ""
                    codelen=0
                    self.count+=1
                    fun.updateProgress(int(10+90*self.count/self.size))
                    fun.refresh()
            except:
                print(current_code)
                exit(0)
        decoded_image = np.array(decoded_image, dtype=np.uint8)
        decoded_image = decoded_image.reshape(self.imshape[0],self.imshape[1],3)
        return decoded_image


    def decompress(self, input_path,fun):
        filename = os.path.splitext(input_path)[0]
        input_path=filename+'.bin'
        output_path = filename + "_decompressed" + ".bmp"
        fun.refresh()
        with open(input_path, 'rb+') as file:
            bit_string = ""
            self.size = len(file.read())
            file.seek(0)
            height = bin(file.read(1)[0])[2:]+bin(file.read(1)[0])[2:].rjust(8,'0')
            width = bin(file.read(1)[0])[2:]+bin(file.read(1)[0])[2:].rjust(8,'0')
            
            self.imshape=(int(height,2),int(width,2),3)
            d_str='{'
            l=file.read(1)[0]
            self.count=5
            while(l):
                ll=ceil(l/8)
                s=''
                for i in range(ll):
                    s+=bin(file.read(1)[0])[2:].rjust(8,'0')
                    self.count+=1
                s=s[-l:]
                d_str+=repr(s)+":"+str((file.read(1)[0],file.read(1)[0],file.read(1)[0]))+","
                self.count+=3
                fun.updateProgress(int(10*self. count/self.size))
                l=file.read(1)[0]
                
            d_str=d_str[:-1]+"}"

            # cp = set(self.reverse_mapping)
            self.reverse_mapping = ast.literal_eval(d_str)
            # s=set(self.reverse_mapping)
            # print(cp.difference(s))
            # print(s.difference(cp))
            
            # print(sorted(s))
            
            # k =list(self.reverse_mapping.keys())
            # l=[len(i) for i in k]
            # s=set(l)
            # s=list(s)
            # s.sort()
            # sum=0
            # d={}
            # for i in s:
            #     r= l.count(i)
            #     sum = sum  + r 
            #     d[i]=r
            
            # print(d,sum)
            

            byte = file.read(1)
            self.count+=1
            while(byte):
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)
                self.count+=1
                fun.updateProgress(int(10*self.count/self.size))
                
        encoded_text = self.remove_padding(bit_string)

        decompressed_text = self.decode_image(encoded_text,fun)
        decoded_img=Image.fromarray(decompressed_text,'RGB')
        decoded_img.save(output_path)
        fun.label.setText("Image Decompressed Successfully!")
        plt.imshow(decoded_img)
        plt.show()
        
        print("Colors:",self.colors)
        
        print("Decompressed")
        return output_path