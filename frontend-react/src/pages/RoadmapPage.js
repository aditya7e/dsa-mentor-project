import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Badge,
  Link,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Checkbox,
  Progress,
  useToast,
  Spinner,
  Center,
} from '@chakra-ui/react';
import { ExternalLinkIcon, LockIcon, CheckCircleIcon } from '@chakra-ui/icons';

const RoadmapPage = ({ roadmap, setRoadmap, onStartNew, onStartWeekTest }) => {
  const [problemsCompleted, setProblemsCompleted] = useState({});
  const [weekProgress, setWeekProgress] = useState({});
  const [loadingWeekTest, setLoadingWeekTest] = useState(null);
  const toast = useToast();

  // Load progress from localStorage on mount
  useEffect(() => {
    const savedProblems = JSON.parse(localStorage.getItem('problemsCompleted') || '{}');
    const savedWeekProgress = JSON.parse(localStorage.getItem('weekProgress') || '{}');
    setProblemsCompleted(savedProblems);
    setWeekProgress(savedWeekProgress);
  }, []);

  // Save progress to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('problemsCompleted', JSON.stringify(problemsCompleted));
  }, [problemsCompleted]);

  const handleProblemCheck = (problemId) => {
    setProblemsCompleted((prev) => ({
      ...prev,
      [problemId]: !prev[problemId],
    }));
  };

  const getWeekCompletionStats = (week) => {
    const completed = week.problems.filter((p) => problemsCompleted[p.id]).length;
    const total = week.problems.length;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    return { completed, total, percentage };
  };

  const isWeekUnlocked = (weekNumber) => {
    if (weekNumber === 1) return true;
    
    const previousWeek = weekNumber - 1;
    return weekProgress[previousWeek]?.passed === true;
  };

  const canTakeWeekTest = (week) => {
    const stats = getWeekCompletionStats(week);
    // Must complete at least 70% of problems to take test
    return stats.percentage >= 70 && !weekProgress[week.week]?.passed;
  };

  const handleTakeWeekTest = async (week) => {
    setLoadingWeekTest(week.week);

    try {
      const response = await fetch(`http://localhost:5000/api/quiz/topic/${encodeURIComponent(week.topic)}`);
      const result = await response.json();

      if (result.status === 'success') {
        toast({
          title: 'Test Generated!',
          description: `Week ${week.week} test is ready.`,
          status: 'success',
          duration: 2000,
          isClosable: true,
        });
        onStartWeekTest(week.week, week.topic, result.data.questions);
      } else {
        throw new Error('Failed to generate test');
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoadingWeekTest(null);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy':
        return 'green';
      case 'Medium':
        return 'yellow';
      case 'Hard':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <Box minH="100vh" bg="gray.50" py={12}>
      <Container maxW="container.lg">
        <VStack spacing={8}>
          {/* Header */}
          <Box textAlign="center">
            <Heading as="h1" size="xl" color="gray.800" mb={2}>
              🗺️ Your Personalized Learning Roadmap
            </Heading>
            <Text fontSize="lg" color="gray.600">
              Complete problems and pass weekly tests to progress
            </Text>
          </Box>

          {/* Roadmap Weeks */}
          <Accordion allowMultiple w="full">
            {roadmap.map((week) => {
              const stats = getWeekCompletionStats(week);
              const unlocked = isWeekUnlocked(week.week);
              const testPassed = weekProgress[week.week]?.passed;
              const canTest = canTakeWeekTest(week);

              return (
                <AccordionItem key={week.week} border="none" mb={4}>
                  <Box
                    bg="white"
                    borderRadius="xl"
                    boxShadow="lg"
                    overflow="hidden"
                    borderLeft="5px solid"
                    borderColor={testPassed ? 'green.500' : unlocked ? 'brand.500' : 'gray.300'}
                    opacity={unlocked ? 1 : 0.6}
                  >
                    <AccordionButton
                      p={6}
                      _hover={{ bg: unlocked ? 'gray.50' : 'gray.100' }}
                      _expanded={{ bg: unlocked ? 'brand.50' : 'gray.100' }}
                      isDisabled={!unlocked}
                    >
                      <Box flex="1" textAlign="left">
                        <HStack spacing={4} mb={2} flexWrap="wrap">
                          <Heading as="h3" size="md" color="gray.800">
                            Week {week.week}: {week.topic}
                          </Heading>
                          
                          {!unlocked && (
                            <Badge colorScheme="gray" fontSize="sm" px={3} py={1}>
                              <LockIcon mr={1} /> Locked
                            </Badge>
                          )}
                          
                          {testPassed && (
                            <Badge colorScheme="green" fontSize="sm" px={3} py={1}>
                              <CheckCircleIcon mr={1} /> Completed
                            </Badge>
                          )}
                          
                          <Badge colorScheme="brand" fontSize="sm" px={3} py={1}>
                            {stats.completed}/{stats.total} Problems
                          </Badge>
                        </HStack>

                        {unlocked && (
                          <Progress
                            value={stats.percentage}
                            size="sm"
                            colorScheme="brand"
                            borderRadius="full"
                            mb={2}
                          />
                        )}

                        <Text color="gray.600" fontSize="sm" fontStyle="italic">
                          📌 {week.focus}
                        </Text>
                      </Box>
                      {unlocked && <AccordionIcon />}
                    </AccordionButton>

                    {unlocked && (
                      <AccordionPanel pb={6} px={6}>
                        {/* Difficulty Distribution */}
                        <HStack spacing={3} mb={6}>
                          {Object.entries(week.difficulty_split).map(
                            ([diff, count]) =>
                              count > 0 && (
                                <Badge
                                  key={diff}
                                  colorScheme={getDifficultyColor(diff)}
                                  fontSize="sm"
                                  px={3}
                                  py={1}
                                >
                                  {count} {diff}
                                </Badge>
                              )
                          )}
                        </HStack>

                        {/* Learning Resources */}
                        {week.learning_resources &&
                          week.learning_resources.length > 0 && (
                            <Box mb={6}>
                              <Text fontWeight="bold" mb={3} color="gray.700">
                                📚 Learning Resources:
                              </Text>
                              <HStack spacing={3} flexWrap="wrap">
                                {week.learning_resources.map((resource, idx) => (
                                  <Link
                                    key={idx}
                                    href={resource.link}
                                    isExternal
                                    bg="brand.500"
                                    color="white"
                                    px={4}
                                    py={2}
                                    borderRadius="lg"
                                    fontSize="sm"
                                    fontWeight="medium"
                                    _hover={{
                                      bg: 'brand.600',
                                      transform: 'translateY(-2px)',
                                      boxShadow: 'md',
                                    }}
                                    transition="all 0.2s"
                                  >
                                    {resource.title} <ExternalLinkIcon mx="2px" />
                                  </Link>
                                ))}
                              </HStack>
                            </Box>
                          )}

                        {/* Problems List */}
                        <VStack spacing={3} align="stretch" mb={6}>
                          {week.problems.map((problem, idx) => (
                            <Box
                              key={problem.id}
                              p={4}
                              bg={problemsCompleted[problem.id] ? 'green.50' : 'gray.50'}
                              borderRadius="lg"
                              borderWidth="1px"
                              borderColor={problemsCompleted[problem.id] ? 'green.200' : 'gray.200'}
                              _hover={{
                                bg: problemsCompleted[problem.id] ? 'green.100' : 'white',
                                borderColor: 'brand.300',
                                boxShadow: 'sm',
                              }}
                              transition="all 0.2s"
                            >
                              <HStack justify="space-between">
                                <HStack spacing={3} flex={1}>
                                  <Checkbox
                                    isChecked={problemsCompleted[problem.id] || false}
                                    onChange={() => handleProblemCheck(problem.id)}
                                    colorScheme="green"
                                    size="lg"
                                  />
                                  <Text fontWeight="medium" color="gray.700">
                                    {idx + 1}.
                                  </Text>
                                  <Text
                                    fontWeight="medium"
                                    color="gray.800"
                                    textDecoration={problemsCompleted[problem.id] ? 'line-through' : 'none'}
                                  >
                                    {problem.name}
                                  </Text>
                                  <Badge
                                    colorScheme={getDifficultyColor(problem.difficulty)}
                                    fontSize="xs"
                                  >
                                    {problem.difficulty}
                                  </Badge>
                                </HStack>
                                <Link
                                  href={problem.link}
                                  isExternal
                                  bg="green.500"
                                  color="white"
                                  px={4}
                                  py={2}
                                  borderRadius="md"
                                  fontSize="sm"
                                  fontWeight="bold"
                                  _hover={{
                                    bg: 'green.600',
                                  }}
                                >
                                  Solve →
                                </Link>
                              </HStack>
                            </Box>
                          ))}
                        </VStack>

                        {/* Week Test Button */}
                        {!testPassed && (
                          <Box
                            bg="purple.50"
                            borderRadius="lg"
                            p={6}
                            borderWidth="2px"
                            borderColor="purple.200"
                          >
                            <VStack spacing={4}>
                              <Text fontWeight="bold" color="purple.800" textAlign="center">
                                📝 Week {week.week} Assessment
                              </Text>
                              <Text fontSize="sm" color="gray.600" textAlign="center">
                                {canTest
                                  ? 'Complete the test to unlock the next week (70% required to pass)'
                                  : `Complete at least 70% of problems (${stats.completed}/${Math.ceil(stats.total * 0.7)} done) to unlock the test`}
                              </Text>

                              {loadingWeekTest === week.week ? (
                                <Center>
                                  <VStack spacing={2}>
                                    <Spinner color="purple.500" />
                                    <Text fontSize="sm" color="gray.600">
                                      Generating test...
                                    </Text>
                                  </VStack>
                                </Center>
                              ) : (
                                <Button
                                  colorScheme="purple"
                                  isDisabled={!canTest}
                                  onClick={() => handleTakeWeekTest(week)}
                                  size="lg"
                                  w="full"
                                >
                                  Take Week {week.week} Test
                                </Button>
                              )}
                            </VStack>
                          </Box>
                        )}
                      </AccordionPanel>
                    )}
                  </Box>
                </AccordionItem>
              );
            })}
          </Accordion>

          {/* Action Button */}
          <Button
            size="lg"
            colorScheme="brand"
            onClick={onStartNew}
            w="full"
            maxW="400px"
          >
            Start New Assessment
          </Button>
        </VStack>
      </Container>
    </Box>
  );
};

export default RoadmapPage;