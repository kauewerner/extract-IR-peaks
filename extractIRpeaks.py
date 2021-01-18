"""
CLI tool to extract IR peaks from jdx files and export as csv

usage: extractIRpeaks.py [-h] [-o OUTPUTFOLDER] [-at AMPTHRESHOLD]
                         [-ef [EXPORTFIGURES]] [-ia INVERTAMPLITUDE]
                         [-if INPUTFORMAT] [-pd PEAKDISTANCE]
                         [-dl CSVDELIMITER]
                         inputFolder

positional arguments:
  inputFolder           Input folder path containing IR data files

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUTFOLDER, --outputFolder OUTPUTFOLDER
                        Path where to output the peak extraction files.
                        Default = './output'
  -at AMPTHRESHOLD, --ampThreshold AMPTHRESHOLD
                        Normalized threshold amplitude for peak extraction.
                        Default = 0.05
  -ef [EXPORTFIGURES], --exportFigures [EXPORTFIGURES]
                        Export results as figures. If not existing, a new
                        folder is created (./figures)
  -ia INVERTAMPLITUDE, --invertAmplitude INVERTAMPLITUDE
                        List of file names to invert amplitude data
                        (transmission instead of absorption). Default =
                        ['none']
  -if INPUTFORMAT, --inputFormat INPUTFORMAT
                        Input file format. Default = 'jdx'
  -pd PEAKDISTANCE, --peakDistance PEAKDISTANCE
                        Distance between array indexes when running the peak
                        extraction. Default = 1
  -dl CSVDELIMITER, --csvDelimiter CSVDELIMITER
                        Column delimiter of csv file. Default = ','
                        
By Kaue Werner 2021
"""
import os
import sys
import argparse
import csv
import numpy as np
from scipy.signal import find_peaks
from jcamp import JCAMP_reader
import matplotlib.pyplot as plt

def list_files(directory,extension):
    return (f for f in os.listdir(directory) if f.endswith(extension))

def create_figure (data,xPeak,yPeak,fileName,outFolder,figdip=72,marker='ob'):
    outFigureFolder = 'figures'
    if not os.path.isdir('.\\'+outFolder+'\\'+outFigureFolder) :
        os.mkdir('.\\'+outFolder+'\\'+outFigureFolder)
        print("\nINFO: A new directory was created for the figures: ./"+ outFolder+"/"+outFigureFolder)
    plt.figure(1,figsize=(15,9),dpi=figdip)
    plt.plot(data[0][:],data[1][:],'-r')
    plt.plot(xPeak,yPeak,marker)
    plt.xlim((400.0,4000.0))
    plt.xlabel('wave number cm-1',fontsize='xx-large')
    plt.ylim((0.0,1.0))
    plt.ylabel('absorption',fontsize='xx-large')
    plt.tick_params(labelsize='xx-large')
    plt.savefig('.\\'+outFolder+'\\'+outFigureFolder+'\\'+fileName)
    plt.clf()
    return 0

def extract_peaks(filesList,outFolder,ampThreshold,invertAmp=['none'],peakDistance=1,csvDelimiter='\t',exportFigures=False):
    for f in filesList :  
        
        # read jdx file
        IRdata = JCAMP_reader('.\\input_IR\\'+f)
        
        # extract wave number (x) and amplitude information (y)
        IRgraph = np.zeros([2,len(IRdata["x"])])
        IRgraph[0][:] = IRdata["x"]
        IRgraph[1][:] = IRdata["y"]
        
        # invert amplitude of specific files
        if f in invertAmp :
            IRgraph[1][:] = 1 - IRgraph[1][:]
        
        # remove offset
        IRgraph[1][:] = IRgraph[1][:] - min(IRgraph[1][:])
        
        # normalize amplitude
        IRgraph[1][:] /= max(IRgraph[1][:])
        
        # find peaks
        peakIdx = find_peaks(IRgraph[1][:],distance=peakDistance)
        peaks = np.zeros([2,len(peakIdx[0])])
        peaks[0][:] = IRgraph[0][np.array(peakIdx[0])]
        peaks[1][:] = IRgraph[1][np.array(peakIdx[0])]
        
        # filter peaks according to amplitude threshold
        peakIdx = np.where(peaks[1][:] >= ampThreshold)
        x = peaks[0][np.array(peakIdx[0])]
        y = peaks[1][np.array(peakIdx[0])]
          
        
        
        # write output files
        if not os.path.isdir('.\\'+outFolder) :
            os.mkdir(outFolder)
            print("\nINFO: A new directory was created for the csv results: ./"+outFolder)
            
        # create figure
        if exportFigures :
            create_figure(IRgraph,x,y,f[:-3],outFolder)
            
        with open('.\\'+ outFolder +'\\'+ f[:-3] +'csv', 'w') as fw:
            writer = csv.writer(fw, delimiter=csvDelimiter)
            writer.writerows(zip(x,y))
            
        print("\nINFO: A total number of "+str(len(peakIdx[0]))+" peaks were extracted from "+f+" IR data")
    return 0

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("inputFolder", help="Input folder path containing IR data files")
    parser.add_argument("-o","--outputFolder", help="Path where to output the peak extraction files. Default = './output_peaks'")
    parser.add_argument("-at", "--ampThreshold", help="Normalized threshold amplitude for peak extraction. Default = 0.05", type=float)
    parser.add_argument("-ef", "--exportFigures",nargs='?', help="Export results as figures. If not existing, a new folder is created (./figures)", const=True , type=bool)
    parser.add_argument("-ia", "--invertAmplitude", help="List of file names to invert amplitude data (transmission instead of absorption). Default = ['none']")
    parser.add_argument("-if", "--inputFormat", help="Input file format. Default = 'jdx'")
    parser.add_argument("-pd", "--peakDistance", help="Distance between array indexes when running the peak extraction. Default = 1",type=int)
    parser.add_argument("-dl", "--csvDelimiter", help="Column delimiter of csv file. Default = ','")
    args = parser.parse_args()
    
    inFolder = args.inputFolder
    outFolder = 'output_peaks' if not args.outputFolder else args.outputFolder
    ampThr = 0.05 if not args.ampThreshold else args.ampThreshold
    exportFigures = False if not args.exportFigures else args.exportFigures
    invAmp = ['none'] if not args.invertAmplitude else args.invertAmplitude
    inputFormat = 'jdx' if not args.inputFormat else args.inputFormat
    peakDistance = 1 if not args.peakDistance else args.peakDistance
    csvDelimiter = ',' if not args.csvDelimiter else args.csvDelimiter
    
    fileNames = list_files(os.getcwd()+'\\'+ inFolder,inputFormat)
    extract_peaks(fileNames,outFolder,ampThr,invertAmp=invAmp,exportFigures=exportFigures,peakDistance=peakDistance,csvDelimiter=csvDelimiter)
    
if __name__ == "__main__":
    main(sys.argv[1:])