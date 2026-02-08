find_package(GTest REQUIRED)
ExternalProject_Add(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG release-1.11.0
)

# A high risk dependency for testing
find_package(HighRiskGPL) # License: GPL-2.0
