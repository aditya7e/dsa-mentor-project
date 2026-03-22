import React, { useState } from 'react';
import { Box } from '@chakra-ui/react';
import LandingPage from './pages/LandingPage';
import QuizPage from './pages/QuizPage';
import ResultsPage from './pages/ResultsPage';
import RoadmapPage from './pages/RoadmapPage';
import WeekTestPage from './pages/WeekTestPage';
import WeekTestResultPage from './pages/WeekTestResultPage';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [quizData, setQuizData] = useState(null);
  const [quizResults, setQuizResults] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  
  // Week test state
  const [currentWeekTest, setCurrentWeekTest] = useState(null);
  const [weekTestData, setWeekTestData] = useState(null);
  const [weekTestResult, setWeekTestResult] = useState(null);

  const goToPage = (page) => {
    setCurrentPage(page);
  };

  return (
    <Box minH="100vh" bg="gray.50">
      {currentPage === 'landing' && (
        <LandingPage 
          onStartQuiz={() => goToPage('quiz')}
          setQuizData={setQuizData}
        />
      )}
      
      {currentPage === 'quiz' && (
        <QuizPage 
          quizData={quizData}
          onComplete={(results) => {
            setQuizResults(results);
            goToPage('results');
          }}
        />
      )}
      
      {currentPage === 'results' && (
        <ResultsPage 
          results={quizResults}
          quizData={quizData}
          onGenerateRoadmap={(roadmapData) => {
            setRoadmap(roadmapData);
            goToPage('roadmap');
          }}
          onRetakeQuiz={() => {
            setQuizData(null);
            setQuizResults(null);
            goToPage('landing');
          }}
        />
      )}
      
      {currentPage === 'roadmap' && (
        <RoadmapPage 
          roadmap={roadmap}
          setRoadmap={setRoadmap}
          onStartNew={() => {
            setQuizData(null);
            setQuizResults(null);
            setRoadmap(null);
            goToPage('landing');
          }}
          onStartWeekTest={(weekNumber, topic, testData) => {
            setCurrentWeekTest(weekNumber);
            setWeekTestData(testData);
            goToPage('weekTest');
          }}
        />
      )}

      {currentPage === 'weekTest' && (
        <WeekTestPage
          week={currentWeekTest}
          quizData={weekTestData}
          onTestComplete={(result) => {
            setWeekTestResult(result);
            goToPage('weekTestResult');
          }}
          onBack={() => goToPage('roadmap')}
        />
      )}

      {currentPage === 'weekTestResult' && (
        <WeekTestResultPage
          week={currentWeekTest}
          result={weekTestResult}
          onContinue={() => {
            // If failed, add more problems to the week
            if (!weekTestResult.passed) {
              // Add 3 more problems to current week
              const updatedRoadmap = [...roadmap];
              const weekIndex = updatedRoadmap.findIndex(w => w.week === currentWeekTest);
              
              if (weekIndex !== -1) {
                // Mark that this week needs more problems
                updatedRoadmap[weekIndex].needsMoreProblems = true;
              }
              
              setRoadmap(updatedRoadmap);
            }
            
            // Save test result to localStorage
            const weekProgress = JSON.parse(localStorage.getItem('weekProgress') || '{}');
            weekProgress[currentWeekTest] = {
              tested: true,
              passed: weekTestResult.passed,
              score: weekTestResult.score,
              percentage: weekTestResult.percentage,
            };
            localStorage.setItem('weekProgress', JSON.stringify(weekProgress));
            
            goToPage('roadmap');
          }}
        />
      )}
    </Box>
  );
}

export default App;