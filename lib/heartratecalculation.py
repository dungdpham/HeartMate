#Class Heartrate Detector:
import math

class Hrv:
    def __init__(self, high_thres = 100, low_thres = 0, window = 37):
        #self.peak = 0
        self.peak_list = []
        self.ppi_list = []
        self.BPM = 0
        self.ppi_s = 0
        ##############################
        self.max_point = 0
        self.max_index = 0
        self.high_thres = high_thres
        self.low_thres = low_thres
        self.window = window
        
    #def add_list(self,value):
        #self.peak_list.append(value)
    
    def detect(self, y, count):
        if y > self.high_thres:
            if y >= self.max_point:
                self.max_point = y
                self.max_index = count
        elif y <= self.low_thres:
            if (count - self.max_index) > self.window:
                if self.max_index not in self.peak_list:
                    self.peak_list.append(self.max_index)
                    self.max_point = 0
            ###########################################################33
                    if len(self.peak_list) >= 2:
                        ppi_diff = self.peak_list[-1] - self.peak_list[-2]
                        
                        #if ppi_diff > 0:
                        ppi_s = ppi_diff*4 #4ms
                        if ppi_s >= 350 and ppi_s <= 2000:
                            self.ppi_list.append(ppi_s)
                            self.ppi_s = ppi_s
                            BPM = 60000/ppi_s
                                #if self.BPM != BPM: 
                            self.BPM = int(BPM)
                            print(f"ppi: {self.ppi_s}, BPM: {self.BPM}bpm")
                            return True
        return False
    
    def analysis(self):
        if len(self.ppi_list) > 0:
            intervals_avg = sum(self.ppi_list)/len(self.ppi_list)
            #print(intervals_avg)
            
            BPM_avg = 60000/intervals_avg
            #print(f'{BPM_avg:.2f}')
            
            s = 0
            for i in range(len(self.ppi_list)-1):
                s += (self.ppi_list[i+1] - self.ppi_list[i])**2
            rmssd = math.sqrt(s/(len(self.ppi_list)-1))   
            
            return intervals_avg, BPM_avg, rmssd
        
        else:
            return 0
        
