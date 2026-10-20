import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

import '../core/config/app_config.dart';

class VideoPlayerScreen extends StatefulWidget {
  final String videoUrl;

  const VideoPlayerScreen({
    super.key,
    required this.videoUrl,
  });

  @override
  State<VideoPlayerScreen> createState() =>
      _VideoPlayerScreenState();
}

class _VideoPlayerScreenState
    extends State<VideoPlayerScreen> {
  late VideoPlayerController controller;

  bool isLoading = true;
  String? errorMessage;

  String get fullVideoUrl {
    final url = widget.videoUrl.trim();

    // Backend already returned a complete URL.
    if (url.startsWith('http://') ||
        url.startsWith('https://')) {
      return url;
    }

    // Backend returned a relative path.
    // Example: /generated/movie.mp4
    if (url.startsWith('/')) {
      return '${AppConfig.baseUrl}$url';
    }

    // Backend returned a path without a leading slash.
    return '${AppConfig.baseUrl}/$url';
  }

  @override
  void initState() {
    super.initState();

    controller = VideoPlayerController.networkUrl(
      Uri.parse(fullVideoUrl),
    );

    initializeVideo();
  }

  Future<void> initializeVideo() async {
    try {
      await controller.initialize();

      if (!mounted) return;

      setState(() {
        isLoading = false;
        errorMessage = null;
      });

      await controller.play();
    } catch (e) {
      if (!mounted) return;

      setState(() {
        isLoading = false;

        errorMessage =
            'Unable to load the movie video.\n\n'
            'Video URL:\n'
            '$fullVideoUrl\n\n'
            'Error:\n'
            '$e';
      });
    }
  }

  Future<void> retryVideo() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    await controller.dispose();

    controller = VideoPlayerController.networkUrl(
      Uri.parse(fullVideoUrl),
    );

    await initializeVideo();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Watch Aadwik Movie',
        ),
      ),
      body: Center(
        child: isLoading
            ? const Column(
                mainAxisAlignment:
                    MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),

                  SizedBox(height: 20),

                  Text(
                    'Loading movie...',
                  ),
                ],
              )
            : errorMessage != null
                ? SingleChildScrollView(
                    padding:
                        const EdgeInsets.all(24),
                    child: Column(
                      mainAxisAlignment:
                          MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.error_outline,
                          size: 64,
                        ),

                        const SizedBox(height: 20),

                        Text(
                          errorMessage!,
                          textAlign:
                              TextAlign.center,
                        ),

                        const SizedBox(height: 24),

                        FilledButton.icon(
                          onPressed: retryVideo,
                          icon: const Icon(
                            Icons.refresh,
                          ),
                          label: const Text(
                            'RETRY VIDEO',
                          ),
                        ),

                        const SizedBox(height: 12),

                        OutlinedButton.icon(
                          onPressed: () {
                            Navigator.pop(context);
                          },
                          icon: const Icon(
                            Icons.arrow_back,
                          ),
                          label: const Text(
                            'GO BACK',
                          ),
                        ),
                      ],
                    ),
                  )
                : AspectRatio(
                    aspectRatio:
                        controller.value.aspectRatio,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        VideoPlayer(
                          controller,
                        ),

                        GestureDetector(
                          onTap: () {
                            if (controller
                                .value
                                .isPlaying) {
                              controller.pause();
                            } else {
                              controller.play();
                            }

                            setState(() {});
                          },
                          child: Container(
                            color:
                                Colors.transparent,
                            alignment:
                                Alignment.center,
                            child: Icon(
                              controller
                                      .value
                                      .isPlaying
                                  ? Icons
                                      .pause_circle_filled
                                  : Icons
                                      .play_circle_fill,
                              size: 72,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
      ),
    );
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }
}