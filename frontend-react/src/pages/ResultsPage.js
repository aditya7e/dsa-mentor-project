import React, { useState } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Progress,
  useToast,
  Spinner,
  Center,
  Divider,
} from '@chakra-ui/react';

const ResultsPage = ({ results, quizData, onGenerateRoadmap, onRetakeQuiz }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const toast = useToast();

  const percentage = Math.round((results.score / results.total) * 100);

  const getScoreColor = () => {
    if (percentage >= 80) return 'green.500';
    if (percentage >= 60) return 'yellow.500';
    return 'red.500';
  };

  const handleGenerateRoadmap = async () => {
    setIsGenerating(true);

    try {
      const response = await fetch('http://localhost:5000/api/roadmap/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_answers: results.userAnswers,
          quiz_questions: quizData,
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        toast({
          title: 'Roadmap Generated!',
          description: 'Your personalized learning path is ready.',
          status: 'success',
          duration: 2000,
          isClosable: true,
        });
        onGenerateRoadmap(data.roadmap);
      } else {
        throw new Error(data.message || 'Failed to generate roadmap');
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsGenerating(false);
    }
  };

  return (
    <Box minH="100vh" bg="gray.50" py={12}>
      <Container maxW="container.md">
        <VStack spacing={8}>
          {/* Header */}
          <Heading as="h1" size="xl" color="gray.800">
            📊 Quiz Results
          </Heading>

          {/* Score Card */}
          <Box
            bg="white"
            borderRadius="xl"
            p={8}
            boxShadow="xl"
            w="full"
            textAlign="center"
          >
            <Box
              bgGradient={`linear(to-br, ${getScoreColor()}, purple.500)`}
              borderRadius="2xl"
              p={8}
              mb={6}
            >
              <Text fontSize="6xl" fontWeight="bold" color="white">
                {results.score}
              </Text>
              <Text fontSize="2xl" color="whiteAlpha.900">
                / {results.total}
              </Text>
              <Text fontSize="3xl" fontWeight="bold" color="white" mt={4}>
                {percentage}%
              </Text>
            </Box>

            <Text fontSize="lg" color="gray.600">
              {percentage >= 80
                ? '🎉 Excellent! You have a strong foundation!'
                : percentage >= 60
                ? '👍 Good job! Keep practicing!'
                : '💪 Keep learning! You can improve!'}
            </Text>
          </Box>

          {/* Topic Breakdown */}
          <Box bg="white" borderRadius="xl" p={8} boxShadow="xl" w="full">
            <Heading as="h2" size="md" mb={6} color="gray.800">
              Topic-wise Performance
            </Heading>

            <VStack spacing={4} align="stretch">
              {Object.entries(results.topicPerformance).map(([topic, stats]) => {
                const topicPercentage = Math.round(
                  (stats.correct / stats.total) * 100
                );

                return (
                  <Box key={topic}>
                    <HStack justify="space-between" mb={2}>
                      <Text fontWeight="medium" color="gray.700">
                        {topic}
                      </Text>
                      <Text fontWeight="bold" color="gray.600">
                        {stats.correct}/{stats.total} ({topicPercentage}%)
                      </Text>
                    </HStack>
                    <Progress
                      value={topicPercentage}
                      colorScheme={
                        topicPercentage >= 70
                          ? 'green'
                          : topicPercentage >= 50
                          ? 'yellow'
                          : 'red'
                      }
                      borderRadius="full"
                      size="sm"
                    />
                  </Box>
                );
              })}
            </VStack>
          </Box>

          <Divider />

          {/* Action Buttons */}
          {isGenerating ? (
            <Center py={8}>
              <VStack spacing={4}>
                <Spinner size="xl" color="brand.500" thickness="4px" />
                <Text color="gray.600" fontWeight="medium">
                  Generating your personalized roadmap...
                </Text>
                <Text fontSize="sm" color="gray.500">
                  This may take 20-40 seconds
                </Text>
              </VStack>
            </Center>
          ) : (
            <VStack spacing={4} w="full">
              <Button
                size="lg"
                colorScheme="brand"
                onClick={handleGenerateRoadmap}
                w="full"
                h="60px"
                fontSize="xl"
                fontWeight="bold"
                boxShadow="lg"
                _hover={{
                  transform: 'translateY(-2px)',
                  boxShadow: '2xl',
                }}
                transition="all 0.2s"
              >
                Get Learning Roadmap →
              </Button>

              <Button
                size="lg"
                variant="outline"
                colorScheme="gray"
                onClick={onRetakeQuiz}
                w="full"
              >
                Take Another Quiz
              </Button>
            </VStack>
          )}
        </VStack>
      </Container>
    </Box>
  );
};

export default ResultsPage;