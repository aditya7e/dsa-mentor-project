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
    onContinue={async () => {
      // If failed, fetch and add more problems
      if (!weekTestResult.passed) {
        const updatedRoadmap = [...roadmap];
        const weekIndex = updatedRoadmap.findIndex(w => w.week === currentWeekTest);
        
        if (weekIndex !== -1) {
          const weekData = updatedRoadmap[weekIndex];
          
          try {
            // Fetch additional problems from backend
            const response = await fetch(
              `http://localhost:5000/api/problems/additional/${encodeURIComponent(weekData.topic)}/mixed`
            );
            const result = await response.json();
            
            if (result.status === 'success' && result.problems.length > 0) {
              // Add new problems to the week
              const newProblems = result.problems.filter(
                newP => !updatedRoadmap[weekIndex].problems.some(existingP => existingP.id === newP.id)
              );
              
              updatedRoadmap[weekIndex].problems = [
                ...updatedRoadmap[weekIndex].problems,
                ...newProblems
              ];
              
              updatedRoadmap[weekIndex].total_problems = updatedRoadmap[weekIndex].problems.length;
              
              // Update difficulty split
              const easyCo = updatedRoadmap[weekIndex].problems.filter(p => p.difficulty === 'Easy').length;
              const mediumCo = updatedRoadmap[weekIndex].problems.filter(p => p.difficulty === 'Medium').length;
              const hardCo = updatedRoadmap[weekIndex].problems.filter(p => p.difficulty === 'Hard').length;
              
              updatedRoadmap[weekIndex].difficulty_split = {
                Easy: easyCo,
                Medium: mediumCo,
                Hard: hardCo
              };
              
              console.log(`Added ${newProblems.length} new problems to Week ${currentWeekTest}`);
            }
          } catch (error) {
            console.error('Failed to fetch additional problems:', error);
          }
          
          setRoadmap(updatedRoadmap);
        }
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