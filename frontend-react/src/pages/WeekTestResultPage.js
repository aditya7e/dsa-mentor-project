import React, { useState } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  Spinner,
  Center,
} from '@chakra-ui/react';

const WeekTestResultPage = ({ week, result, onContinue }) => {
  const [isLoading, setIsLoading] = useState(false);
  const { score, total, percentage, passed } = result;

  const handleContinue = async () => {
    setIsLoading(true);
    await onContinue();
    setIsLoading(false);
  };

  return (
    <Box minH="100vh" bg="gray.50" py={12}>
      <Container maxW="container.md">
        <VStack spacing={8}>
          {/* Result Card */}
          <Box
            bg="white"
            borderRadius="xl"
            p={8}
            boxShadow="xl"
            w="full"
            textAlign="center"
          >
            <Box
              bgGradient={
                passed
                  ? 'linear(to-br, green.500, green.600)'
                  : 'linear(to-br, orange.500, red.500)'
              }
              borderRadius="2xl"
              p={8}
              mb={6}
            >
              <Text fontSize="6xl" fontWeight="bold" color="white">
                {score}
              </Text>
              <Text fontSize="2xl" color="whiteAlpha.900">
                / {total}
              </Text>
              <Text fontSize="3xl" fontWeight="bold" color="white" mt={4}>
                {percentage}%
              </Text>
            </Box>

            {passed ? (
              <VStack spacing={4}>
                <Heading as="h2" size="lg" color="green.600">
                  🎉 Congratulations!
                </Heading>
                <Text fontSize="lg" color="gray.600">
                  You passed Week {week} test! You can now move to the next week.
                </Text>
              </VStack>
            ) : (
              <VStack spacing={4}>
                <Heading as="h2" size="lg" color="orange.600">
                  📚 Keep Practicing
                </Heading>
                <Text fontSize="lg" color="gray.600">
                  You scored below 70%. We're adding more problems to Week {week}{' '}
                  to help you improve.
                </Text>
                <Text fontSize="md" color="gray.500">
                  Complete the additional problems and retake the test.
                </Text>
              </VStack>
            )}
          </Box>

          {/* Action Button */}
          {isLoading ? (
            <Center py={8}>
              <VStack spacing={4}>
                <Spinner size="xl" color="brand.500" thickness="4px" />
                <Text color="gray.600" fontWeight="medium">
                  {passed ? 'Returning to roadmap...' : 'Adding more problems...'}
                </Text>
              </VStack>
            </Center>
          ) : (
            <Button
              size="lg"
              colorScheme={passed ? 'green' : 'orange'}
              onClick={handleContinue}
              w="full"
              maxW="400px"
            >
              {passed ? 'Continue to Roadmap →' : 'Back to Week ' + week}
            </Button>
          )}
        </VStack>
      </Container>
    </Box>
  );
};

export default WeekTestResultPage;