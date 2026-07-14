import React, { useState, useCallback, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileVideo, ChevronRight, Activity } from 'lucide-react';
import * as faceapi from '@vladmandic/face-api';

const StaggeredText = ({ text }) => {
  const words = text.split(" ");
  
  const container = {
    hidden: { opacity: 0 },
    visible: (i = 1) => ({
      opacity: 1,
      transition: { staggerChildren: 0.05, delayChildren: 0.04 * i },
    }),
  };

  const child = {
    visible: { opacity: 1, y: 0, filter: "blur(0px)", transition: { type: "spring", damping: 12, stiffness: 100 } },
    hidden: { opacity: 0, y: 20, filter: "blur(10px)", transition: { type: "spring", damping: 12, stiffness: 100 } },
  };

  return (
    <motion.div style={{ overflow: "hidden", display: "flex", flexWrap: "wrap", justifyContent: "center" }} variants={container} initial="hidden" animate="visible">
      {words.map((word, index) => (
        <motion.span variants={child} style={{ marginRight: "0.25em" }} key={index}>{word}</motion.span>
      ))}
    </motion.div>
  );
};

export default function App() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [score, setScore] = useState(null);
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [logMsgs, setLogMsgs] = useState([]);
  const videoRef = useRef(null);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/';
        await faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL);
        await faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL);
        setModelsLoaded(true);
      } catch (err) {
        console.error("Error loading face-api models", err);
      }
    };
    loadModels();
  }, []);

  const fileInputRef = useRef(null);

  const handleDragOver = useCallback((e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(true); }, []);
  const handleDragLeave = useCallback((e) => { e.preventDefault(); e.stopPropagation(); setIsDragging(false); }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type.startsWith('video/') || droppedFile.name.endsWith('.mp4'))) {
      setFile(droppedFile);
      setScore(null);
      setLogMsgs([]);
    } else {
      alert("Please drop a valid .mp4 video file.");
    }
  }, []);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setScore(null);
      setLogMsgs([]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const addLog = (msg) => setLogMsgs(prev => [...prev.slice(-3), msg]);

  const handleAnalyze = async () => {
    if (!modelsLoaded) {
      alert("Still loading ML models, please wait...");
      return;
    }
    setIsAnalyzing(true);
    addLog("Mounting video file...");

    const videoUrl = URL.createObjectURL(file);
    const videoEl = document.createElement('video');
    videoEl.src = videoUrl;
    videoEl.muted = true;
    videoEl.playsInline = true;

    // Use a canvas to force the browser to decode the frame even if hidden
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    videoEl.onloadeddata = async () => {
      canvas.width = videoEl.videoWidth;
      canvas.height = videoEl.videoHeight;
      addLog("Extracting frames and processing...");
      let totalHappy = 0;
      let totalNeutral = 0;
      let totalFaces = 0;
      let duration = videoEl.duration;

      for (let i = 1; i <= 10; i++) {
        videoEl.currentTime = (duration / 11) * i;
        
        // Wait for the video to finish seeking
        await new Promise((resolve) => {
          videoEl.onseeked = resolve;
          // Fallback if onseeked doesn't fire
          setTimeout(resolve, 500);
        });

        // Draw the exact frame to canvas
        ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
        
        addLog(`Analyzing frame ${i}/10...`);
        
        const detections = await faceapi.detectSingleFace(canvas, new faceapi.SsdMobilenetv1Options()).withFaceExpressions();
        if (detections) {
          totalFaces++;
          totalHappy += detections.expressions.happy || 0;
          totalNeutral += detections.expressions.neutral || 0;
        }
      }

      let finalScore = 50; 
      if (totalFaces > 0) {
        let avgHappy = totalHappy / totalFaces;
        let avgNeutral = totalNeutral / totalFaces;
        addLog(`Detected smiles: ${(avgHappy*100).toFixed(1)}%`);
        
        // Boost the weighting so scores are higher on average (since people don't smile 100% of the time)
        finalScore = Math.min(99, Math.max(0, (avgHappy * 120) + (avgNeutral * 50) + 30));
      } else {
        addLog("No faces detected in video!");
        finalScore = 15; // Penalty for no face
      }

      setIsAnalyzing(false);
      setScore(Math.round(finalScore));
    };
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-black flex flex-col items-center justify-center p-6">
      <div className="absolute inset-0 glow pointer-events-none z-0"></div>
      
      <div className="z-10 w-full max-w-2xl flex flex-col items-center text-center">
        <div className="mb-8">
          <motion.div className="inline-block px-4 py-1.5 mb-6 rounded-full border border-white/10 bg-white/5 backdrop-blur-md text-sm text-gray-300 font-medium tracking-wide uppercase">
            {modelsLoaded ? "Engine Ready" : "Loading Weights..."}
          </motion.div>
          
          <h1 className="text-4xl md:text-6xl font-semibold tracking-tight text-white mb-6">
            <StaggeredText text="Infer the unspoken critical elements." />
          </h1>
        </div>

        {/* Hidden Video element for real inference */}
        <video ref={videoRef} style={{ display: 'none' }} muted />

        <AnimatePresence mode="wait">
          {!file ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={triggerFileInput}
              className={`w-full p-12 border-2 border-dashed rounded-3xl backdrop-blur-2xl flex flex-col items-center cursor-pointer group ${isDragging ? 'border-white/40 bg-white/10' : 'border-white/10 bg-white/[0.02]'}`}
            >
              <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="video/*,.mp4" className="hidden" />
              <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-6">
                <UploadCloud className="text-white/60 w-8 h-8" />
              </div>
              <h3 className="text-xl font-medium text-white mb-2">Drag & Drop your .mp4</h3>
              <p className="text-gray-500 text-sm">Or click to browse local files</p>
            </motion.div>
          ) : !score ? (
            <motion.div key="analyze" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="w-full p-8 border border-white/10 rounded-3xl bg-white/5 backdrop-blur-2xl flex flex-col items-center">
              <div className="flex items-center space-x-4 mb-8 w-full bg-black/40 p-4 rounded-2xl border border-white/5">
                <FileVideo className="text-blue-400 w-6 h-6" />
                <div className="text-left flex-1">
                  <p className="text-white font-medium">{file.name}</p>
                </div>
              </div>
              
              <button onClick={handleAnalyze} disabled={isAnalyzing || !modelsLoaded} className="px-8 py-4 text-white bg-white/10 rounded-full w-full">
                {isAnalyzing ? (
                  <div className="flex flex-col items-center">
                    <Activity className="w-5 h-5 animate-pulse text-blue-400 mb-2" />
                    <span className="text-sm text-blue-300">{logMsgs[logMsgs.length - 1] || "Extracting Frames..."}</span>
                  </div>
                ) : "Run Face-API Analysis"}
              </button>
            </motion.div>
          ) : (
             <motion.div key="result" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="w-full p-12 border border-white/10 rounded-3xl bg-blue-900/20 backdrop-blur-2xl flex flex-col items-center relative">
              <p className="text-gray-400 text-sm font-semibold mb-4">Charisma & Warmth Score</p>
              <div className="text-7xl font-light text-white mb-6">{score}<span className="text-blue-500">%</span></div>
              <p className="text-gray-400 text-sm max-w-md">Score calculated from real face-api.js expression extraction across 10 temporal frames.</p>
              <button onClick={() => setFile(null)} className="mt-8 text-white/50 hover:text-white border-b border-white/10 pb-1">Analyze another video</button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
