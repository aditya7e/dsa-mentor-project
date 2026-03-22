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
  Center,
} from '@chakra-ui/react';

const WeekTestPage = ({ week, quizData, onTestComplete, onBack }) => {
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

    // Calculate score
    let score = 0;
    quizData.forEach((q, index) => {
      if (userAnswers[index] === q.correct_answer) {
        score++;
      }
    });

    const percentage = Math.round((score / quizData.length) * 100);

    onTestComplete({
      score,
      total: quizData.length,
      percentage,
      passed: percentage >= 70,
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
        {/* Header */}
        <VStack spacing={4} mb={8}>
          <Badge colorScheme="purple" fontSize="lg" px={4} py={2}>
            Week {week} Test
          </Badge>
          <Heading as="h1" size="lg" color="gray.800" textAlign="center">
            Complete this test to unlock the next week
          </Heading>
          <Text color="gray.600" textAlign="center">
            You need 70% or higher to pass
          </Text>
        </VStack>

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
                Submit Test ✓
              </Button>
            ) : (
              <Button onClick={handleNext} colorScheme="brand" size="lg">
                Next →
              </Button>
            )}
          </HStack>
        </Box>

        {/* Back Button */}
        <Center mt={6}>
          <Button variant="ghost" onClick={onBack}>
            ← Back to Roadmap
          </Button>
        </Center>
      </Container>
    </Box>
  );
};

export default WeekTestPage;