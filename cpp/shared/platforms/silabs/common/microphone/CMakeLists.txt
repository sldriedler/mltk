
set(NAME mltk_sl_mic)
add_library(${NAME})


target_sources(${NAME}
PRIVATE
  sl_mic_i2s.c
)


target_link_libraries(${NAME}
PRIVATE
  ${MLTK_PLATFORM}
  mltk::cpputils
  mltk::gecko_sdk::dmadrv
  mltk::gecko_sdk::includes
)
