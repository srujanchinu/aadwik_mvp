import 'dart:convert';

import 'package:http/http.dart' as http;

import '../core/config/app_config.dart';
import '../models/movie.dart';

class MovieService {
  Uri _uri(String path) {
    return Uri.parse('${AppConfig.baseUrl}$path');
  }

  // ==========================================================
  // CREATE MOVIE
  // ==========================================================

  Future<Movie> createMovie({
    required String prompt,
    required String style,
    required String language,
    required int durationMinutes,
    required String genre,
    required String ageGroup,
    required String characterType,
    required String musicMood,
    required String platform,
    required bool talkingAnimals,
    required bool lipSync,
    required bool sceneBasedMusic,
    required bool soundEffects,
    required bool subtitles,
    required bool autoGenerateThumbnail,
    required String thumbnailStyle,
    required String thumbnailTitle,
    required String thumbnailExpression,
    required bool includeMainCharacter,
  }) async {
    String aspectRatio = '16:9';

    switch (platform) {
      case 'YouTube Shorts':
      case 'Instagram Reel':
      case 'Facebook Reel':
        aspectRatio = '9:16';
        break;

      case 'Instagram Feed Portrait':
        aspectRatio = '4:5';
        break;

      case 'Instagram Feed Square':
        aspectRatio = '1:1';
        break;

      default:
        aspectRatio = '16:9';
    }

    final r = await http
        .post(
          _uri('/movies'),
          headers: {
            'Content-Type': 'application/json',
          },
          body: jsonEncode({
            'prompt': prompt,
            'style': style,
            'language': language,
            'duration_minutes': durationMinutes,
            'genre': genre,
            'age_group': ageGroup,
            'character_type': characterType,
            'platform': platform,
            'aspect_ratio': aspectRatio,
            'talking_animals': talkingAnimals,
            'lip_sync': lipSync,
            'music_mood': musicMood,
            'scene_based_music': sceneBasedMusic,
            'sound_effects': soundEffects,
            'subtitles': subtitles,
            'auto_generate_thumbnail': autoGenerateThumbnail,
            'thumbnail_style': thumbnailStyle,
            'thumbnail_title': thumbnailTitle,
            'thumbnail_expression': thumbnailExpression,
            'include_main_character': includeMainCharacter,
          }),
        )
        .timeout(const Duration(minutes: 2));

    if (r.statusCode < 200 || r.statusCode >= 300) {
      throw Exception(_message(r));
    }

    return Movie.fromJson(
      jsonDecode(r.body),
    );
  }

  // ==========================================================
  // GET ALL MOVIES
  // ==========================================================

  Future<List<Movie>> listMovies() async {
    final r = await http
        .get(
          _uri('/movies'),
        )
        .timeout(const Duration(seconds: 20));

    if (r.statusCode != 200) {
      throw Exception(_message(r));
    }

    final data = jsonDecode(r.body) as List<dynamic>;

    return data
        .map(
          (movie) => Movie.fromJson(
            movie as Map<String, dynamic>,
          ),
        )
        .toList();
  }

  // ==========================================================
  // GET MOVIE STATUS
  // ==========================================================

  Future<Movie> status(String id) async {
    final r = await http
        .get(
          _uri('/movies/$id'),
        )
        .timeout(const Duration(seconds: 15));

    if (r.statusCode != 200) {
      throw Exception(_message(r));
    }

    return Movie.fromJson(
      jsonDecode(r.body),
    );
  }

  // ==========================================================
  // CANCEL MOVIE
  // ==========================================================

  Future<Movie> cancel(String id) async {
    final r = await http
        .post(
          _uri('/movies/$id/cancel'),
        )
        .timeout(const Duration(seconds: 15));

    if (r.statusCode != 200) {
      throw Exception(_message(r));
    }

    return Movie.fromJson(
      jsonDecode(r.body),
    );
  }

  // ==========================================================
  // APPROVE MOVIE
  // ==========================================================

  Future<Movie> approveMovie(
    String movieId, {
    String reason = '',
  }) async {
    return _updateApproval(
      movieId: movieId,
      action: 'APPROVE',
      reason: reason,
    );
  }

  // ==========================================================
  // NEEDS REVIEW
  // ==========================================================

  Future<Movie> needsReview(
    String movieId, {
    String reason = '',
  }) async {
    return _updateApproval(
      movieId: movieId,
      action: 'NEEDS_REVIEW',
      reason: reason,
    );
  }

  // ==========================================================
  // REJECT MOVIE
  // ==========================================================

  Future<Movie> rejectMovie(
    String movieId, {
    String reason = '',
  }) async {
    return _updateApproval(
      movieId: movieId,
      action: 'REJECT',
      reason: reason,
    );
  }

  // ==========================================================
  // COMMON APPROVAL REQUEST
  // ==========================================================

  Future<Movie> _updateApproval({
    required String movieId,
    required String action,
    required String reason,
  }) async {
    if (movieId.trim().isEmpty) {
      throw Exception('Movie ID is missing.');
    }

    final r = await http
        .post(
          _uri('/movies/$movieId/approval'),
          headers: {
            'Content-Type': 'application/json',
          },
          body: jsonEncode({
            'action': action,
            'reason': reason,
          }),
        )
        .timeout(const Duration(seconds: 20));

    if (r.statusCode < 200 || r.statusCode >= 300) {
      throw Exception(_message(r));
    }

    return Movie.fromJson(
      jsonDecode(r.body),
    );
  }

  // ==========================================================
  // REQUEST CHANGES
  // ==========================================================

  Future<Movie> requestChanges({
    required String movieId,
    String reason = '',
  }) async {
    return needsReview(
      movieId,
      reason: reason,
    );
  }

  // ==========================================================
  // SCHEDULE MOVIE
  // ==========================================================

  Future<Movie> scheduleMovie({
    required String movieId,
    required String scheduledAt,
    required String platform,
    String timezone = 'Asia/Kolkata',
  }) async {
    final r = await http
        .post(
          _uri('/movies/$movieId/schedule'),
          headers: {
            'Content-Type': 'application/json',
          },
          body: jsonEncode({
            'scheduled_at': scheduledAt,
            'platform': platform,
            'timezone': timezone,
          }),
        )
        .timeout(const Duration(seconds: 20));

    if (r.statusCode < 200 || r.statusCode >= 300) {
      throw Exception(_message(r));
    }

    return Movie.fromJson(
      jsonDecode(r.body),
    );
  }

  // ==========================================================
  // AUTO STORY
  // ==========================================================

  Future<Map<String, dynamic>> autoStory({
  String niche = 'Auto',
  String language = 'Auto',
  String ageGroup = 'Auto',
}) async {
  final r = await http
      .post(
        _uri('/movies/auto-story'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'niche': niche,
          'language': language,
          'age_group': ageGroup,
        }),
      )
      .timeout(const Duration(minutes: 2));

  if (r.statusCode < 200 || r.statusCode >= 300) {
    throw Exception(_message(r));
  }

  return jsonDecode(r.body) as Map<String, dynamic>;
}

  // ==========================================================
  // ERROR MESSAGE
  // ==========================================================

  String _message(http.Response r) {
    try {
      return (
        jsonDecode(r.body)['detail'] ??
        r.body
      ).toString();
    } catch (_) {
      return 'Network error (${r.statusCode})';
    }
  }
}