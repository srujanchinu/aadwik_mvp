import 'dart:async';

import 'package:flutter/material.dart';

import '../models/movie.dart';
import '../services/movie_service.dart';
import 'create_movie_screen.dart';
import 'generation_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() =>
      _HomeScreenState();
}

class _HomeScreenState
    extends State<HomeScreen> {
  final MovieService service =
      MovieService();

  bool loading = true;
  String? error;

  List<Movie> movies = [];

  Timer? refreshTimer;

  @override
  void initState() {
    super.initState();

    loadMovies();

    refreshTimer = Timer.periodic(
      const Duration(seconds: 3),
      (_) {
        if (!mounted) {
          return;
        }

        final hasGeneratingMovie =
            movies.any(
          (movie) => _isGenerating(movie),
        );

        if (hasGeneratingMovie) {
          loadMovies(
            showLoading: false,
          );
        }
      },
    );
  }

  // ==========================================================
  // LOAD MOVIES
  // ==========================================================

  Future<void> loadMovies({
    bool showLoading = true,
  }) async {
    if (showLoading) {
      setState(() {
        loading = true;
        error = null;
      });
    }

    try {
      final loadedMovies =
          await service.listMovies();

      if (!mounted) {
        return;
      }

      setState(() {
        movies = loadedMovies;
        loading = false;
        error = null;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }

      setState(() {
        error =
            'Unable to load your movies.';
        loading = false;
      });
    }
  }

  // ==========================================================
  // CHECK GENERATION STATUS
  // ==========================================================

  bool _isGenerating(
    Movie movie,
  ) {
    final status =
        movie.status.toLowerCase().trim();

    return status == 'processing' ||
        status == 'generating' ||
        status == 'queued' ||
        status == 'pending';
  }

  // ==========================================================
  // CHECK SCHEDULE STATUS
  // ==========================================================

  bool _isScheduled(
    Movie movie,
  ) {
    return movie.scheduleStatus
            .toUpperCase()
            .trim() ==
        'SCHEDULED';
  }

  // ==========================================================
  // FORMAT SCHEDULE DATE
  // ==========================================================

  String _formatScheduledDateTime(
    String? value,
  ) {
    if (value == null ||
        value.trim().isEmpty) {
      return 'Schedule time not available';
    }

    try {
      final dateTime =
          DateTime.parse(value).toLocal();

      final hour =
          dateTime.hour == 0
              ? 12
              : dateTime.hour > 12
                  ? dateTime.hour - 12
                  : dateTime.hour;

      final minute =
          dateTime.minute
              .toString()
              .padLeft(2, '0');

      final period =
          dateTime.hour >= 12
              ? 'PM'
              : 'AM';

      return '${dateTime.day}/${dateTime.month}/${dateTime.year} at $hour:$minute $period';
    } catch (_) {
      return value;
    }
  }

  // ==========================================================
  // OPEN CREATE MOVIE
  // ==========================================================

  Future<void>
      openCreateMovie() async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) =>
            const CreateMovieScreen(),
      ),
    );

    loadMovies();
  }

  // ==========================================================
  // OPEN MOVIE
  // ==========================================================

  Future<void> openMovie(
    Movie movie,
  ) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) =>
            GenerationScreen(
          movieId:
              movie.movieId,
        ),
      ),
    );

    loadMovies();
  }

  // ==========================================================
  // MOVIE TITLE
  // ==========================================================

  String movieTitle(
    Movie movie,
  ) {
    if (movie
        .thumbnailTitle
        .trim()
        .isNotEmpty) {
      return movie
          .thumbnailTitle
          .trim();
    }

    final prompt =
        movie.prompt.trim();

    if (prompt.isNotEmpty) {
      if (prompt.length <= 42) {
        return prompt;
      }

      return '${prompt.substring(0, 42)}...';
    }

    return 'Untitled Aadwik Movie';
  }

  // ==========================================================
  // MOVIE PREVIEW
  // ==========================================================

  String moviePreview(
    Movie movie,
  ) {
    final prompt =
        movie.prompt.trim();

    if (prompt.isEmpty) {
      return 'No story preview available.';
    }

    if (prompt.length <= 110) {
      return prompt;
    }

    return '${prompt.substring(0, 110)}...';
  }

  // ==========================================================
  // STATUS LABEL
  // ==========================================================

  String statusLabel(
    String status,
  ) {
    switch (
        status.toLowerCase().trim()) {
      case 'completed':
        return 'COMPLETED';

      case 'cancelled':
        return 'CANCELLED';

      case 'failed':
        return 'FAILED';

      case 'processing':
      case 'generating':
        return 'GENERATING';

      case 'queued':
      case 'pending':
        return 'WAITING';

      default:
        return status.toUpperCase();
    }
  }

  // ==========================================================
  // STATUS ICON
  // ==========================================================

  IconData statusIcon(
    String status,
  ) {
    switch (
        status.toLowerCase().trim()) {
      case 'completed':
        return Icons.check_circle;

      case 'cancelled':
        return Icons.cancel;

      case 'failed':
        return Icons.error;

      case 'queued':
      case 'pending':
        return Icons.hourglass_top;

      default:
        return Icons.auto_awesome;
    }
  }

  // ==========================================================
  // DURATION LABEL
  // ==========================================================

  String durationLabel(
    Movie movie,
  ) {
    final minutes =
        movie.durationMinutes;

    if (minutes <= 0) {
      return '—';
    }

    return '$minutes min';
  }

  // ==========================================================
  // BUILD SCREEN
  // ==========================================================

  @override
  Widget build(
    BuildContext context,
  ) {
    final isEmpty =
        !loading &&
            error == null &&
            movies.isEmpty;

    return Scaffold(
      appBar: AppBar(
        title:
            const Text('AADWIK AI'),
        actions: [
          IconButton(
            onPressed: loading
                ? null
                : () => loadMovies(),
            icon: const Icon(
              Icons.refresh,
            ),
            tooltip:
                'Refresh movies',
          ),
        ],
      ),

      floatingActionButton:
          isEmpty
              ? null
              : FloatingActionButton
                  .extended(
                  onPressed:
                      openCreateMovie,
                  icon:
                      const Icon(
                    Icons.add,
                  ),
                  label:
                      const Text(
                    'CREATE MOVIE',
                  ),
                ),

      body: RefreshIndicator(
        onRefresh: () =>
            loadMovies(),
        child: loading
            ? const Center(
                child:
                    CircularProgressIndicator(),
              )
            : error != null
                ? _buildErrorState()
                : movies.isEmpty
                    ? _buildEmptyState()
                    : _buildMovieLibrary(),
      ),
    );
  }

  // ==========================================================
  // EMPTY STATE
  // ==========================================================

  Widget _buildEmptyState() {
    return ListView(
      physics:
          const AlwaysScrollableScrollPhysics(),
      children: [
        SizedBox(
          height:
              MediaQuery.of(context)
                      .size
                      .height *
                  0.75,
          child: Center(
            child: Padding(
              padding:
                  const EdgeInsets.all(
                24,
              ),
              child: Column(
                mainAxisAlignment:
                    MainAxisAlignment
                        .center,
                children: [
                  const Icon(
                    Icons
                        .movie_creation_outlined,
                    size: 88,
                  ),

                  const SizedBox(
                    height: 24,
                  ),

                  const Text(
                    'Your Aadwik Movie Library',
                    style:
                        TextStyle(
                      fontSize: 28,
                      fontWeight:
                          FontWeight
                              .bold,
                    ),
                    textAlign:
                        TextAlign
                            .center,
                  ),

                  const SizedBox(
                    height: 12,
                  ),

                  const Text(
                    'Create your first AI movie. Your movies will appear here.',
                    textAlign:
                        TextAlign
                            .center,
                  ),

                  const SizedBox(
                    height: 28,
                  ),

                  FilledButton.icon(
                    onPressed:
                        openCreateMovie,
                    icon:
                        const Icon(
                      Icons
                          .movie_creation,
                    ),
                    label:
                        const Padding(
                      padding:
                          EdgeInsets
                              .symmetric(
                        horizontal:
                            12,
                        vertical:
                            14,
                      ),
                      child: Text(
                        'CREATE YOUR FIRST MOVIE',
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  // ==========================================================
  // ERROR STATE
  // ==========================================================

  Widget _buildErrorState() {
    return ListView(
      physics:
          const AlwaysScrollableScrollPhysics(),
      children: [
        SizedBox(
          height:
              MediaQuery.of(context)
                      .size
                      .height *
                  0.75,
          child: Center(
            child: Padding(
              padding:
                  const EdgeInsets.all(
                24,
              ),
              child: Column(
                mainAxisAlignment:
                    MainAxisAlignment
                        .center,
                children: [
                  const Icon(
                    Icons
                        .cloud_off_outlined,
                    size: 72,
                  ),

                  const SizedBox(
                    height: 20,
                  ),

                  const Text(
                    'Unable to load movies',
                    style:
                        TextStyle(
                      fontSize: 22,
                      fontWeight:
                          FontWeight
                              .bold,
                    ),
                  ),

                  const SizedBox(
                    height: 10,
                  ),

                  Text(
                    error ??
                        'Something went wrong.',
                    textAlign:
                        TextAlign
                            .center,
                  ),

                  const SizedBox(
                    height: 24,
                  ),

                  FilledButton.icon(
                    onPressed: () =>
                        loadMovies(),
                    icon:
                        const Icon(
                      Icons.refresh,
                    ),
                    label:
                        const Text(
                      'TRY AGAIN',
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  // ==========================================================
  // MOVIE LIBRARY
  // ==========================================================

  Widget _buildMovieLibrary() {
    return ListView(
      physics:
          const AlwaysScrollableScrollPhysics(),
      padding:
          const EdgeInsets.fromLTRB(
        16,
        20,
        16,
        100,
      ),
      children: [
        const Text(
          'YOUR MOVIES',
          style: TextStyle(
            fontSize: 24,
            fontWeight:
                FontWeight.bold,
          ),
        ),

        const SizedBox(
          height: 6,
        ),

        Text(
          '${movies.length} movie${movies.length == 1 ? '' : 's'} in your library',
        ),

        const SizedBox(
          height: 20,
        ),

        ...movies.map(
          (movie) =>
              _buildMovieCard(
            movie,
          ),
        ),
      ],
    );
  }

  // ==========================================================
  // MOVIE CARD
  // ==========================================================

  Widget _buildMovieCard(
    Movie movie,
  ) {
    final status =
        statusLabel(
      movie.status,
    );

    final isGenerating =
        _isGenerating(movie);

    final isScheduled =
        _isScheduled(movie);

    final progress =
        movie.progress
            .clamp(
              0,
              100,
            )
            .toInt();

    return Card(
      margin:
          const EdgeInsets.only(
        bottom: 16,
      ),
      child: InkWell(
        borderRadius:
            BorderRadius.circular(
          12,
        ),
        onTap: () =>
            openMovie(movie),
        child: Padding(
          padding:
              const EdgeInsets.all(
            18,
          ),
          child: Column(
            crossAxisAlignment:
                CrossAxisAlignment
                    .start,
            children: [

              // ============================================
              // TITLE
              // ============================================

              Row(
                crossAxisAlignment:
                    CrossAxisAlignment
                        .start,
                children: [
                  Icon(
                    statusIcon(
                      movie.status,
                    ),
                    size: 36,
                  ),

                  const SizedBox(
                    width: 14,
                  ),

                  Expanded(
                    child: Column(
                      crossAxisAlignment:
                          CrossAxisAlignment
                              .start,
                      children: [
                        Text(
                          movieTitle(
                            movie,
                          ),
                          style:
                              const TextStyle(
                            fontSize: 20,
                            fontWeight:
                                FontWeight
                                    .bold,
                          ),
                        ),

                        const SizedBox(
                          height: 6,
                        ),

                        Text(
                          status,
                          style:
                              const TextStyle(
                            fontSize: 13,
                            fontWeight:
                                FontWeight
                                    .bold,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const Icon(
                    Icons.chevron_right,
                  ),
                ],
              ),

              const SizedBox(
                height: 16,
              ),

              // ============================================
              // STORY PREVIEW
              // ============================================

              Text(
                moviePreview(
                  movie,
                ),
                maxLines: 3,
                overflow:
                    TextOverflow
                        .ellipsis,
              ),

              const SizedBox(
                height: 18,
              ),

              // ============================================
              // MOVIE SETTINGS
              // ============================================

              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildChip(
                    Icons
                        .category_outlined,
                    movie.genre.isEmpty
                        ? 'Movie'
                        : movie.genre,
                  ),

                  _buildChip(
                    Icons.language,
                    movie.language.isEmpty
                        ? 'Language'
                        : movie.language,
                  ),

                  _buildChip(
                    Icons.animation,
                    movie.style.isEmpty
                        ? 'AI Animation'
                        : movie.style,
                  ),

                  _buildChip(
                    Icons.aspect_ratio,
                    movie.aspectRatio,
                  ),

                  _buildChip(
                    Icons.schedule,
                    durationLabel(
                      movie,
                    ),
                  ),
                ],
              ),

              const SizedBox(
                height: 18,
              ),

              // ============================================
              // SCHEDULE INFORMATION
              // ============================================

              if (isScheduled) ...[
                Container(
                  width: double.infinity,
                  padding:
                      const EdgeInsets.all(
                    14,
                  ),
                  decoration:
                      BoxDecoration(
                    border: Border.all(
                      color:
                          Theme.of(
                        context,
                      )
                              .colorScheme
                              .outline,
                    ),
                    borderRadius:
                        BorderRadius.circular(
                      12,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment:
                        CrossAxisAlignment
                            .start,
                    children: [

                      Row(
                        children: [
                          const Icon(
                            Icons
                                .calendar_month,
                          ),

                          const SizedBox(
                            width: 8,
                          ),

                          const Text(
                            'SCHEDULED',
                            style:
                                TextStyle(
                              fontWeight:
                                  FontWeight
                                      .bold,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(
                        height: 12,
                      ),

                      Row(
                        children: [
                          const Icon(
                            Icons
                                .play_circle_outline,
                            size: 18,
                          ),

                          const SizedBox(
                            width: 8,
                          ),

                          Expanded(
                            child: Text(
                              'Platform: ${movie.scheduledPlatform?.isNotEmpty == true ? movie.scheduledPlatform : movie.platform}',
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(
                        height: 8,
                      ),

                      Row(
                        children: [
                          const Icon(
                            Icons.schedule,
                            size: 18,
                          ),

                          const SizedBox(
                            width: 8,
                          ),

                          Expanded(
                            child: Text(
                              _formatScheduledDateTime(
                                movie.scheduledAt,
                              ),
                            ),
                          ),
                        ],
                      ),

                      if (movie
                              .scheduleTimezone
                              ?.isNotEmpty ==
                          true) ...[
                        const SizedBox(
                          height: 8,
                        ),

                        Row(
                          children: [
                            const Icon(
                              Icons.public,
                              size: 18,
                            ),

                            const SizedBox(
                              width: 8,
                            ),

                            Expanded(
                              child: Text(
                                movie.scheduleTimezone!,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),

                const SizedBox(
                  height: 18,
                ),
              ],

              // ============================================
              // GENERATION PROGRESS
              // ============================================

              if (isGenerating) ...[
                Row(
                  children: [
                    Expanded(
                      child:
                          ClipRRect(
                        borderRadius:
                            BorderRadius
                                .circular(
                          8,
                        ),
                        child:
                            LinearProgressIndicator(
                          value:
                              progress /
                                  100,
                          minHeight:
                              10,
                        ),
                      ),
                    ),

                    const SizedBox(
                      width: 14,
                    ),

                    Text(
                      '$progress%',
                      style:
                          const TextStyle(
                        fontWeight:
                            FontWeight
                                .bold,
                      ),
                    ),
                  ],
                ),

                const SizedBox(
                  height: 14,
                ),
              ],

              // ============================================
              // CURRENT STEP
              // ============================================

              Row(
                children: [
                  Icon(
                    movie.status
                                .toLowerCase()
                                .trim() ==
                            'completed'
                        ? Icons
                            .play_circle_outline
                        : isGenerating
                            ? Icons
                                .auto_awesome
                            : statusIcon(
                                movie.status,
                              ),
                    size: 20,
                  ),

                  const SizedBox(
                    width: 8,
                  ),

                  Expanded(
                    child: Text(
                      movie.status
                                  .toLowerCase()
                                  .trim() ==
                              'completed'
                          ? isScheduled
                              ? 'Movie scheduled for publishing'
                              : 'Movie ready to watch'
                          : isGenerating
                              ? (movie.currentStep ??
                                  'Movie generation in progress')
                              : movie.currentStep ??
                                  status,
                    ),
                  ),
                ],
              ),

              const SizedBox(
                height: 14,
              ),

              // ============================================
              // MOVIE ID + SCENES
              // ============================================

              Row(
                children: [
                  Expanded(
                    child: Text(
                      'Movie ID: ${movie.movieId.length > 10 ? '${movie.movieId.substring(0, 10)}...' : movie.movieId}',
                      style:
                          Theme.of(
                        context,
                      )
                              .textTheme
                              .bodySmall,
                    ),
                  ),

                  Text(
                    '${movie.scenes.length} scene${movie.scenes.length == 1 ? '' : 's'}',
                    style:
                        Theme.of(
                      context,
                    )
                            .textTheme
                            .bodySmall,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ==========================================================
  // CHIP
  // ==========================================================

  Widget _buildChip(
    IconData icon,
    String label,
  ) {
    return Container(
      padding:
          const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 8,
      ),
      decoration:
          BoxDecoration(
        border: Border.all(
          color:
              Theme.of(context)
                  .colorScheme
                  .outline,
        ),
        borderRadius:
            BorderRadius.circular(
          10,
        ),
      ),
      child: Row(
        mainAxisSize:
            MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 18,
          ),

          const SizedBox(
            width: 6,
          ),

          Text(
            label,
          ),
        ],
      ),
    );
  }

  // ==========================================================
  // DISPOSE
  // ==========================================================

  @override
  void dispose() {
    refreshTimer?.cancel();

    super.dispose();
  }
}