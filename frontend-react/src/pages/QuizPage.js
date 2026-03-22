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
  Badge,
  Radio,
  RadioGroup,
  Stack,
  useToast,
} from '@chakra-ui/react';

const QuizPage = ({ quizData, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [userAnswers, setUserAnswers] = useState(new Array(quizData.length).fill(null));
  const toast = useToast();

  const question = quizData[currentQuestion];
  const progress = ((currentQuestion + 1) / quizData.length) * 100;

  const handleAnswer = (answer) => {
    const newAnswers = [...userAnswers];
    newAnswers[currentQuestion] = answer;
    setUserAnswers(newAnswers);
  };

  const handleNext = () => {
    if (!userAnswers[currentQuestion]) {
      toast({
        title: 'Please select an answer',
        status: 'warning',
        duration: 2000,
        isClosable: true,
      });
      return;
    }

    if (currentQuestion < quizData.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = () => {
    if (!userAnswers[currentQuestion]) {
      toast({
        title: 'Please select an answer',
        status: 'warning',
        duration: 2000,
        isClosable: true,
      });
      return;
    }

    // Calculate results
    let score = 0;
    let topicPerformance = {};

    quizData.forEach((q, index) => {
      const isCorrect = userAnswers[index] === q.correct_answer;
      if (isCorrect) score++;

      if (!topicPerformance[q.topic]) {
        topicPerformance[q.topic] = { correct: 0, total: 0 };
      }
      topicPerformance[q.topic].total++;
      if (isCorrect) topicPerformance[q.topic].correct++;
    });

    onComplete({
      score,
      total: quizData.length,
      topicPerformance,
      userAnswers,
    });
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
    <Box minH="100vh" bg="gray.50" py={8}>
      <Container maxW="container.lg">
        {/* Progress Bar */}
        <Box mb={8}>
          <Progress
            value={progress}
            size="sm"
            colorScheme="brand"
            borderRadius="full"
            mb={2}
          />
          <Text fontSize="sm" color="gray.600" textAlign="right">
            {currentQuestion + 1} / {quizData.length}
          </Text>
        </Box>

        {/* Question Card */}
        <Box bg="white" borderRadius="xl" p={8} boxShadow="xl">
          {/* Header */}
          <HStack justify="space-between" mb={6}>
            <Text fontSize="lg" fontWeight="bold" color="brand.500">
              Question {currentQuestion + 1}
            </Text>
            <Badge
              colorScheme={getDifficultyColor(question.difficulty)}
              fontSize="md"
              px={3}
              py={1}
              borderRadius="full"
            >
              {question.difficulty}
            </Badge>
          </HStack>

          {/* Question */}
          <Heading as="h2" size="md" mb={8} color="gray.800">
            {question.question}
          </Heading>

          {/* Options */}
          <RadioGroup
            value={userAnswers[currentQuestion]}
            onChange={handleAnswer}
            mb={8}
          >
            <Stack spacing={4}>
              {question.options.map((option, index) => {
                const optionLetter = String.fromCharCode(65 + index);
                return (
                  <Box
                    key={index}
                    p={4}
                    borderWidth="2px"
                    borderRadius="lg"
                    borderColor={
                      userAnswers[currentQuestion] === optionLetter
                        ? 'brand.500'
                        : 'gray.200'
                    }
                    bg={
                      userAnswers[currentQuestion] === optionLetter
                        ? 'brand.50'
                        : 'white'
                    }
                    cursor="pointer"
                    transition="all 0.2s"
                    _hover={{
                      borderColor: 'brand.300',
                      bg: 'gray.50',
                    }}
                    onClick={() => handleAnswer(optionLetter)}
                  >
                    <Radio value={optionLetter} colorScheme="brand">
                      <Text fontSize="md">{option}</Text>
                    </Radio>
                  </Box>
                );
              })}
            </Stack>
          </RadioGroup>

          {/* Navigation */}
          <HStack justify="space-between">
            <Button
              onClick={handlePrevious}
              isDisabled={currentQuestion === 0}
              variant="outline"
              colorScheme="gray"
              size="lg"
            >
              ← Previous
            </Button>

            {currentQuestion === quizData.length - 1 ? (
              <Button
                onClick={handleSubmit}
                colorScheme="green"
                size="lg"
                fontWeight="bold"
              >
                Submit Quiz ✓
              </Button>
            ) : (
              <Button
                onClick={handleNext}
                colorScheme="brand"
                size="lg"
              >
                Next →
              </Button>
            )}
          </HStack>
        </Box>
      </Container>
    </Box>
  );
};

export default QuizPage;