import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileVideo, ChevronRight, Activity } from 'lucide-react';

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
    visible: {
      opacity: 1,
      y: 0,
      filter: "blur(0px)",
      transition: { type: "spring", damping: 12, stiffness: 100 },
    },
    hidden: {
      opacity: 0,
      y: 20,
      filter: "blur(10px)",
      transition: { type: "spring", damping: 12, stiffness: 100 },
    },
  };

  return (
    <motion.div
      style={{ overflow: "hidden", display: "flex", flexWrap: "wrap", justifyContent: "center" }}
      variants={container}
      initial="hidden"
      animate="visible"
    >
      {words.map((word, index) => (
        <motion.span variants={child} style={{ marginRight: "0.25em" }} key={index}>
          {word}
        </motion.span>
      ))}
    </motion.div>
  );
};

export default function App() {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [score, setScore] = useState(null);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('video/')) {
      setFile(droppedFile);
    }
  }, []);

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    // Simulate analyzing via Embedding/Multimodal API
    setTimeout(() => {
      setIsAnalyzing(false);
      setScore(87);
    }, 3000);
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-black flex flex-col items-center justify-center p-6">
      {/* Absolute Glow Background */}
      <div className="absolute inset-0 glow pointer-events-none z-0"></div>
      
      <div className="z-10 w-full max-w-2xl flex flex-col items-center text-center">
        
        <div className="mb-8">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }} 
            animate={{ opacity: 1, scale: 1 }} 
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="inline-block px-4 py-1.5 mb-6 rounded-full border border-white/10 bg-white/5 backdrop-blur-md text-sm text-gray-300 font-medium tracking-wide uppercase"
          >
            The Subtext Engine
          </motion.div>
          
          <h1 className="text-4xl md:text-6xl font-semibold tracking-tight text-white mb-6">
            <StaggeredText text="Infer the unspoken critical elements." />
          </h1>
          
          <p className="text-gray-400 text-lg max-w-xl mx-auto leading-relaxed">
            <StaggeredText text="Drop your 1-minute intro video below. We convert it into a high-dimensional multimodal embedding and compare its latent subtext against the historical cluster of admitted scholars. 100% private, processed in-memory." />
          </p>
        </div>

        <AnimatePresence mode="wait">
          {!file ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.5 }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`w-full p-12 border-2 border-dashed rounded-3xl transition-all duration-300 backdrop-blur-2xl flex flex-col items-center justify-center cursor-pointer group
                ${isDragging 
                  ? 'border-white/40 bg-white/10 shadow-[0_0_40px_rgba(255,255,255,0.1)]' 
                  : 'border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]'
                }`}
            >
              <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <UploadCloud className="text-white/60 w-8 h-8" />
              </div>
              <h3 className="text-xl font-medium text-white mb-2">Drag & Drop your .mp4</h3>
              <p className="text-gray-500 text-sm">or click to browse local files</p>
            </motion.div>
          ) : !score ? (
            <motion.div
              key="analyze"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full p-8 border border-white/10 rounded-3xl bg-white/5 backdrop-blur-2xl flex flex-col items-center"
            >
              <div className="flex items-center space-x-4 mb-8 w-full bg-black/40 p-4 rounded-2xl border border-white/5">
                <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                  <FileVideo className="text-blue-400 w-6 h-6" />
                </div>
                <div className="text-left flex-1 overflow-hidden">
                  <p className="text-white font-medium truncate">{file.name}</p>
                  <p className="text-gray-500 text-sm">{(file.size / (1024 * 1024)).toFixed(2)} MB • Ready for inference</p>
                </div>
              </div>
              
              <button 
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="group relative inline-flex items-center justify-center px-8 py-4 font-medium text-white bg-white/10 border border-white/20 rounded-full overflow-hidden transition-all hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed w-full md:w-auto"
              >
                {isAnalyzing ? (
                  <div className="flex items-center space-x-3">
                    <Activity className="w-5 h-5 animate-pulse text-blue-400" />
                    <span>Extracting Embeddings...</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <span>Calculate Standout Factor</span>
                    <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </div>
                )}
              </button>
            </motion.div>
          ) : (
             <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full p-12 border border-white/10 rounded-3xl bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black backdrop-blur-2xl flex flex-col items-center relative overflow-hidden"
            >
              <div className="absolute top-[-150px] w-full h-[150px] bg-blue-500/20 blur-[100px]"></div>
              
              <p className="text-gray-400 uppercase tracking-widest text-sm font-semibold mb-4">Standout Probability</p>
              <div className="text-7xl font-light text-white mb-6 tracking-tighter">
                {score}<span className="text-blue-500">%</span>
              </div>
              
              <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden mb-8">
                <motion.div 
                  initial={{ width: 0 }} 
                  animate={{ width: `${score}%` }} 
                  transition={{ duration: 1.5, ease: "easeOut" }}
                  className="h-full bg-blue-500"
                ></motion.div>
              </div>
              
              <p className="text-gray-400 text-sm leading-relaxed max-w-md">
                Cosine similarity high. The latent space representations of your subtext (pacing, environment, warmth) align tightly with the historical admitted cluster.
              </p>
              
              <button 
                onClick={() => { setFile(null); setScore(null); }}
                className="mt-8 text-white/50 hover:text-white transition-colors text-sm border-b border-white/10 pb-1"
              >
                Reset & analyze another video
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
