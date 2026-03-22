import React, { useState } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  List,
  ListItem,
  ListIcon,
  useToast,
  Spinner,
  Center,
} from '@chakra-ui/react';
import { CheckCircleIcon } from '@chakra-ui/icons';

const LandingPage = ({ onStartQuiz, setQuizData }) => {
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  const handleGenerateQuiz = async () => {
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/quiz/generate');
      const result = await response.json();

      if (result.status === 'success') {
        setQuizData(result.data.questions);
        toast({
          title: 'Quiz Generated!',
          description: '30 questions ready for you.',
          status: 'success',
          duration: 2000,
          isClosable: true,
        });
        setTimeout(() => onStartQuiz(), 500);
      } else {
        throw new Error('Failed to generate quiz');
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsLoading(false);
    }
  };

  return (
    <Box
      minH="100vh"
      bgGradient="linear(to-br, brand.500, purple.600)"
      display="flex"
      alignItems="center"
      justifyContent="center"
      py={12}
    >
      <Container maxW="container.md">
        <VStack spacing={8} textAlign="center">
          <Heading
            as="h1"
            size="2xl"
            color="white"
            fontWeight="bold"
            textShadow="0 2px 10px rgba(0,0,0,0.2)"
          >
            🎯 DSA Mentor
          </Heading>

          <Text fontSize="xl" color="whiteAlpha.900" fontWeight="medium">
            Master Data Structures & Algorithms with AI-powered personalized learning
          </Text>

          <Box
            bg="white"
            borderRadius="xl"
            p={8}
            boxShadow="2xl"
            w="full"
          >
            <Heading as="h2" size="lg" mb={4} color="gray.800">
              Ready to test your DSA knowledge?
            </Heading>

            <Text color="gray.600" mb={6}>
              Take our comprehensive 30-question quiz covering:
            </Text>

            <List spacing={3} textAlign="left" mb={8}>
              <ListItem>
                <ListIcon as={CheckCircleIcon} color="brand.500" />
                Arrays & Strings
              </ListItem>
              <ListItem>
                <ListIcon as={CheckCircleIcon} color="brand.500" />
                Linked Lists & Trees
              </ListItem>
              <ListItem>
                <ListIcon as={CheckCircleIcon} color="brand.500" />
                Graphs & Dynamic Programming
              </ListItem>
              <ListItem>
                <ListIcon as={CheckCircleIcon} color="brand.500" />
                Sorting, Searching & Advanced Topics
              </ListItem>
            </List>

            {isLoading ? (
              <Center py={8}>
                <VStack spacing={4}>
                  <Spinner size="xl" color="brand.500" thickness="4px" />
                  <Text color="gray.600" fontWeight="medium">
                    Generating personalized quiz...
                  </Text>
                </VStack>
              </Center>
            ) : (
              <Button
                size="lg"
                colorScheme="brand"
                onClick={handleGenerateQuiz}
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
                Generate Quiz
              </Button>
            )}
          </Box>
        </VStack>
      </Container>
    </Box>
  );
};

export default LandingPage;