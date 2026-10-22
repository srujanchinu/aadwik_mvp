import 'dart:async';

import 'package:flutter/material.dart';

import '../models/movie.dart';
import '../services/movie_service.dart';
import 'scene_breakdown_screen.dart';
import 'schedule_movie_screen.dart';
import 'video_player_screen.dart';

class GenerationScreen extends StatefulWidget {
  final String movieId;

  const GenerationScreen({
    super.key,
    required this.movieId,
  });

  @override
  State<GenerationScreen> createState() =>
      _GenerationScreenState();
}

class _GenerationScreenState
    extends State<GenerationScreen> {
  final service = MovieService();

  Timer? timer;
  Movie? movie;

  String? lastError;

  bool cancelling = false;
  bool approving = false;

  @override
  void initState() {
    super.initState();

    load();

    timer = Timer.periodic(
      const Duration(seconds: 3),
      (_) => load(),
    );
  }

  Future<void> load() async {
    try {
      final m = await service.status(
        widget.movieId,
      );

      if (!mounted) return;

      setState(() {
        movie = m;
        lastError = null;
      });

      if (m.status == 'cancelled' ||
          m.status == 'completed') {
        timer?.cancel();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          lastError =
              'Unable to refresh progress. '
              'Check backend connection.';
        });
      }
    }
  }

  Future<void> cancel() async {
    setState(() {
      cancelling = true;
    });

    try {
      await service.cancel(
        widget.movieId,
      );

      await load();
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(
          const SnackBar(
            content: Text(
              'Could not cancel generation.',
            ),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          cancelling = false;
        });
      }
    }
  }

  Future<void> updateApproval(
    String action, {
    String? reason,
  }) async {
    if (approving) return;

    setState(() {
      approving = true;
    });

    try {
      Movie updatedMovie;

      switch (action) {
        case 'APPROVE':
          updatedMovie =
              await service.approveMovie(
            widget.movieId,
            reason: reason ?? '',
          );
          break;

        case 'NEEDS_REVIEW':
          updatedMovie =
              await service.needsReview(
            widget.movieId,
            reason: reason ?? '',
          );
          break;

        case 'REJECT':
          updatedMovie =
              await service.rejectMovie(
            widget.movieId,
            reason: reason ?? '',
          );
          break;

        default:
          throw Exception(
            'Invalid approval action.',
          );
      }

      if (!mounted) return;

      setState(() {
        movie = updatedMovie;
      });

      String message;

      switch (action) {
        case 'APPROVE':
          message =
              'Movie approved successfully! ✅';
          break;

        case 'NEEDS_REVIEW':
          message =
              'Movie marked for review. 🟡';
          break;

        case 'REJECT':
          message =
              'Movie rejected. ❌';
          break;

        default:
          message =
              'Approval status updated.';
      }

      ScaffoldMessenger.of(context)
          .showSnackBar(
        SnackBar(
          content: Text(message),
        ),
      );

      await load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(
          SnackBar(
            content: Text(
              'Could not update approval: $e',
            ),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          approving = false;
        });
      }
    }
  }

  Future<String?> askForReason({
    required String title,
    required String hint,
  }) async {
    final controller =
        TextEditingController();

    final result =
        await showDialog<String>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: Text(title),
          content: TextField(
            controller: controller,
            maxLines: 3,
            decoration: InputDecoration(
              hintText: hint,
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(
                  dialogContext,
                );
              },
              child: const Text(
                'CANCEL',
              ),
            ),
            FilledButton(
              onPressed: () {
                Navigator.pop(
                  dialogContext,
                  controller.text.trim(),
                );
              },
              child: const Text(
                'CONTINUE',
              ),
            ),
          ],
        );
      },
    );

    controller.dispose();

    return result;
  }

  Future<void> approveMovie() async {
    final reason =
        await askForReason(
      title: 'Approve Movie',
      hint:
          'Optional approval note...',
    );

    if (reason == null) return;

    await updateApproval(
      'APPROVE',
      reason: reason.isEmpty
          ? null
          : reason,
    );
  }

  Future<void> markNeedsReview() async {
    final reason =
        await askForReason(
      title: 'Needs Review',
      hint:
          'Why does this movie need review?',
    );

    if (reason == null) return;

    await updateApproval(
      'NEEDS_REVIEW',
      reason: reason.isEmpty
          ? null
          : reason,
    );
  }

  Future<void> rejectMovie() async {
    final reason =
        await askForReason(
      title: 'Reject Movie',
      hint:
          'Why is this movie rejected?',
    );

    if (reason == null) return;

    await updateApproval(
      'REJECT',
      reason: reason.isEmpty
          ? null
          : reason,
    );
  }

  // ==========================================================
  // OPEN SCHEDULING SCREEN
  // ==========================================================

  Future<void> readyForSchedule() async {
    final approvalStatus =
        movie?.approvalStatus ??
            'PENDING_REVIEW';

    if (approvalStatus != 'APPROVED') {
      String message;

      switch (approvalStatus) {
        case 'NEEDS_REVIEW':
          message =
              'This movie needs review before scheduling. 🟡';
          break;

        case 'REJECTED':
          message =
              'Rejected movies cannot be scheduled. ❌';
          break;

        default:
          message =
              'This movie must be approved before scheduling. 🟡';
      }

      ScaffoldMessenger.of(context)
          .showSnackBar(
        SnackBar(
          content: Text(message),
        ),
      );

      return;
    }

    if (movie == null) {
      return;
    }

    final result =
        await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (context) =>
            ScheduleMovieScreen(
          movie: movie!,
        ),
      ),
    );

    if (!mounted) return;

    if (result == true) {
      Navigator.pop(
        context,
        true,
      );
    }
  }

  void openVideoPlayer() {
    final videoPath =
        movie?.videoPath;

    if (videoPath == null ||
        videoPath.isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(
        const SnackBar(
          content: Text(
            'Movie video is not available yet.',
          ),
        ),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            VideoPlayerScreen(
          videoUrl: videoPath,
        ),
      ),
    );
  }

  void openSceneBreakdown() {
    if (movie == null) {
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            SceneBreakdownScreen(
          scenes: movie!.scenes,
        ),
      ),
    );
  }

  Widget buildApprovalStatus() {
    final status =
        movie?.approvalStatus ??
            'PENDING_REVIEW';

    IconData icon;
    String label;

    switch (status) {
      case 'APPROVED':
        icon = Icons.verified;
        label = 'APPROVED';
        break;

      case 'NEEDS_REVIEW':
        icon =
            Icons.warning_amber_rounded;
        label = 'NEEDS REVIEW';
        break;

      case 'REJECTED':
        icon =
            Icons.cancel_outlined;
        label = 'REJECTED';
        break;

      default:
        icon =
            Icons.pending_actions;
        label = 'PENDING REVIEW';
    }

    return Card(
      child: Padding(
        padding:
            const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisSize:
                  MainAxisSize.min,
              children: [
                Icon(icon),

                const SizedBox(
                  width: 10,
                ),

                Text(
                  'Approval: $label',
                  style:
                      const TextStyle(
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),
              ],
            ),

            if (movie
                    ?.approvalReason !=
                null) ...[
              const SizedBox(
                height: 10,
              ),
              Text(
                movie!.approvalReason!,
                textAlign:
                    TextAlign.center,
              ),
            ],

            if (movie
                    ?.autoApproved ==
                true) ...[
              const SizedBox(
                height: 8,
              ),
              const Text(
                'Automatically approved',
              ),
            ],
          ],
        ),
      ),
    );
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    final p =
        movie?.progress ?? 0;

    final cancelled =
        movie?.status ==
            'cancelled';

    final completed =
        movie?.status ==
            'completed';

    final hasScenes =
        movie != null &&
            movie!
                .scenes
                .isNotEmpty;

    final approvalStatus =
        movie?.approvalStatus ??
            'PENDING_REVIEW';

    return Scaffold(
      appBar: AppBar(
        title: Text(
          completed
              ? 'Movie Ready'
              : cancelled
                  ? 'Generation Cancelled'
                  : 'Aadwik is Generating',
        ),
      ),
      body: SingleChildScrollView(
        padding:
            const EdgeInsets.all(24),
        child: Center(
          child: Column(
            mainAxisAlignment:
                MainAxisAlignment.center,
            children: [
              Icon(
                completed
                    ? Icons.check_circle
                    : cancelled
                        ? Icons
                            .cancel_outlined
                        : Icons
                            .auto_awesome_motion,
                size: 88,
              ),

              const SizedBox(
                height: 28,
              ),

              Text(
                '$p%',
                style:
                    const TextStyle(
                  fontSize: 42,
                  fontWeight:
                      FontWeight.bold,
                ),
              ),

              const SizedBox(
                height: 16,
              ),

              LinearProgressIndicator(
                value: p / 100,
                minHeight: 12,
              ),

              const SizedBox(
                height: 24,
              ),

              Text(
                movie?.currentStep ??
                    'Preparing AI pipeline...',
                textAlign:
                    TextAlign.center,
              ),

              if (lastError != null)
                Padding(
                  padding:
                      const EdgeInsets.only(
                    top: 16,
                  ),
                  child: Text(
                    lastError!,
                    textAlign:
                        TextAlign.center,
                  ),
                ),

              const SizedBox(
                height: 24,
              ),

              if (hasScenes &&
                  !cancelled) ...[
                OutlinedButton.icon(
                  onPressed:
                      openSceneBreakdown,
                  icon: const Icon(
                    Icons
                        .movie_filter_outlined,
                  ),
                  label: const Text(
                    'VIEW SCENE BREAKDOWN',
                  ),
                ),

                const SizedBox(
                  height: 16,
                ),
              ],

              if (completed) ...[
                const Text(
                  'Movie Generation Completed! 🎉',
                  style:
                      TextStyle(
                    fontSize: 22,
                    fontWeight:
                        FontWeight.bold,
                  ),
                  textAlign:
                      TextAlign.center,
                ),

                const SizedBox(
                  height: 12,
                ),

                const Text(
                  'Your Aadwik movie is ready.',
                  textAlign:
                      TextAlign.center,
                ),

                const SizedBox(
                  height: 20,
                ),

                FilledButton.icon(
                  onPressed:
                      openVideoPlayer,
                  icon: const Icon(
                    Icons.play_arrow,
                  ),
                  label: const Text(
                    'WATCH MOVIE',
                  ),
                ),

                const SizedBox(
                  height: 16,
                ),

                buildApprovalStatus(),

                const SizedBox(
                  height: 16,
                ),

                if (approvalStatus !=
                    'APPROVED') ...[
                  FilledButton.icon(
                    onPressed:
                        approving
                            ? null
                            : approveMovie,
                    icon: approving
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child:
                                CircularProgressIndicator(
                              strokeWidth:
                                  2,
                            ),
                          )
                        : const Icon(
                            Icons
                                .check_circle,
                          ),
                    label: Text(
                      approving
                          ? 'UPDATING...'
                          : 'APPROVE MOVIE',
                    ),
                  ),

                  const SizedBox(
                    height: 12,
                  ),
                ],

                if (approvalStatus !=
                    'NEEDS_REVIEW') ...[
                  OutlinedButton.icon(
                    onPressed:
                        approving
                            ? null
                            : markNeedsReview,
                    icon: const Icon(
                      Icons
                          .warning_amber_rounded,
                    ),
                    label: const Text(
                      'NEEDS REVIEW',
                    ),
                  ),

                  const SizedBox(
                    height: 12,
                  ),
                ],

                if (approvalStatus !=
                    'REJECTED') ...[
                  OutlinedButton.icon(
                    onPressed:
                        approving
                            ? null
                            : rejectMovie,
                    icon: const Icon(
                      Icons.cancel_outlined,
                    ),
                    label: const Text(
                      'REJECT MOVIE',
                    ),
                  ),

                  const SizedBox(
                    height: 12,
                  ),
                ],

                // READY FOR SCHEDULE
                OutlinedButton.icon(
                  onPressed:
                      approving
                          ? null
                          : readyForSchedule,
                  icon: const Icon(
                    Icons.schedule,
                  ),
                  label: const Text(
                    'READY FOR SCHEDULE',
                  ),
                ),
              ] else if (!cancelled)
                OutlinedButton.icon(
                  onPressed:
                      cancelling
                          ? null
                          : cancel,
                  icon: const Icon(
                    Icons
                        .stop_circle_outlined,
                  ),
                  label: Text(
                    cancelling
                        ? 'CANCELLING...'
                        : 'CANCEL GENERATION',
                  ),
                ),

              const SizedBox(
                height: 10,
              ),

              Text(
                'Movie ID: '
                '${widget.movieId}',
                style:
                    Theme.of(context)
                        .textTheme
                        .bodySmall,
                textAlign:
                    TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }
}
