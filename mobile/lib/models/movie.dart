class Scene {
  final int sceneNumber;
  final String title;
  final String description;
  final List<String> characters;
  final String dialogue;
  final String emotion;
  final String visualDirection;
  final String cameraDirection;
  final String musicMood;
  final List<String> soundEffects;
  final int estimatedDurationSeconds;

  // Scene production status
  final String status;
  final String productionStep;
  final int sceneProgress;

  Scene({
    required this.sceneNumber,
    required this.title,
    required this.description,
    required this.characters,
    required this.dialogue,
    required this.emotion,
    required this.visualDirection,
    required this.cameraDirection,
    required this.musicMood,
    required this.soundEffects,
    required this.estimatedDurationSeconds,
    required this.status,
    required this.productionStep,
    required this.sceneProgress,
  });

  factory Scene.fromJson(
    Map<String, dynamic> json,
  ) {
    return Scene(
      sceneNumber:
          json['scene_number'] ?? 0,
      title:
          json['title'] ?? '',
      description:
          json['description'] ?? '',
      characters:
          List<String>.from(
        json['characters'] ?? [],
      ),
      dialogue:
          json['dialogue'] ?? '',
      emotion:
          json['emotion'] ?? '',
      visualDirection:
          json['visual_direction'] ?? '',
      cameraDirection:
          json['camera_direction'] ?? '',
      musicMood:
          json['music_mood'] ?? '',
      soundEffects:
          List<String>.from(
        json['sound_effects'] ?? [],
      ),
      estimatedDurationSeconds:
          json[
                  'estimated_duration_seconds'
              ] ??
              0,

      status:
          json['status'] ?? 'PLANNED',

      productionStep:
          json['production_step'] ??
              'Waiting for production.',

      sceneProgress:
          json['progress'] ?? 0,
    );
  }
}

class Movie {
  // ==========================================================
  // CORE MOVIE STATUS
  // ==========================================================

  final String movieId;
  final String status;
  final int progress;
  final String? currentStep;
  final String? videoPath;
  final String? error;
  final String createdAt;

  // ==========================================================
  // MOVIE INFORMATION
  // ==========================================================

  final String prompt;
  final String style;
  final String language;
  final int durationMinutes;

  // ==========================================================
  // CONTENT SETTINGS
  // ==========================================================

  final String genre;
  final String ageGroup;
  final String characterType;

  // ==========================================================
  // AUDIO SETTINGS
  // ==========================================================

  final String musicMood;
  final bool sceneBasedMusic;
  final bool soundEffects;

  // ==========================================================
  // PLATFORM SETTINGS
  // ==========================================================

  final String platform;
  final String aspectRatio;

  // ==========================================================
  // CHARACTER SETTINGS
  // ==========================================================

  final bool talkingAnimals;
  final bool lipSync;

  // ==========================================================
  // ACCESSIBILITY
  // ==========================================================

  final bool subtitles;

  // ==========================================================
  // THUMBNAIL SETTINGS
  // ==========================================================

  final bool autoGenerateThumbnail;
  final String thumbnailStyle;
  final String thumbnailTitle;
  final String thumbnailExpression;
  final bool includeMainCharacter;

  // ==========================================================
  // APPROVAL WORKFLOW
  // ==========================================================

  final String approvalStatus;
  final String? approvalReason;
  final String? reviewedAt;
  final bool autoApproved;

  // ==========================================================
  // SCHEDULING WORKFLOW
  // ==========================================================

  final String scheduleStatus;
  final String? scheduledAt;
  final String? scheduledPlatform;
  final String? scheduleTimezone;

  // ==========================================================
  // SCENES
  // ==========================================================

  final List<Scene> scenes;

  Movie({
    // Core movie status
    required this.movieId,
    required this.status,
    required this.progress,
    this.currentStep,
    this.videoPath,
    this.error,
    required this.createdAt,

    // Movie information
    required this.prompt,
    required this.style,
    required this.language,
    required this.durationMinutes,

    // Content settings
    required this.genre,
    required this.ageGroup,
    required this.characterType,

    // Audio settings
    required this.musicMood,
    required this.sceneBasedMusic,
    required this.soundEffects,

    // Platform settings
    required this.platform,
    required this.aspectRatio,

    // Character settings
    required this.talkingAnimals,
    required this.lipSync,

    // Accessibility
    required this.subtitles,

    // Thumbnail settings
    required this.autoGenerateThumbnail,
    required this.thumbnailStyle,
    required this.thumbnailTitle,
    required this.thumbnailExpression,
    required this.includeMainCharacter,

    // Approval workflow
    required this.approvalStatus,
    this.approvalReason,
    this.reviewedAt,
    required this.autoApproved,

    // Scheduling workflow
    required this.scheduleStatus,
    this.scheduledAt,
    this.scheduledPlatform,
    this.scheduleTimezone,

    // Scenes
    required this.scenes,
  });

  // ==========================================================
  // JSON
  // ==========================================================

  factory Movie.fromJson(
    Map<String, dynamic> json,
  ) {
    return Movie(
      // Core status
      movieId:
          json['movie_id'] ?? '',

      status:
          json['status'] ?? '',

      progress:
          json['progress'] ?? 0,

      currentStep:
          json['current_step'],

      videoPath:
          json['video_path'],

      error:
          json['error'],

      createdAt:
          json['created_at'] ?? '',

      // Movie information
      prompt:
          json['prompt'] ?? '',

      style:
          json['style'] ?? '',

      language:
          json['language'] ?? '',

      durationMinutes:
          json['duration_minutes'] ?? 0,

      // Content settings
      genre:
          json['genre'] ?? '',

      ageGroup:
          json['age_group'] ?? '',

      characterType:
          json['character_type'] ?? '',

      // Audio settings
      musicMood:
          json['music_mood'] ?? '',

      sceneBasedMusic:
          json['scene_based_music'] ?? true,

      soundEffects:
          json['sound_effects'] ?? true,

      // Platform settings
      platform:
          json['platform'] ?? '',

      aspectRatio:
          json['aspect_ratio'] ?? '16:9',

      // Character settings
      talkingAnimals:
          json['talking_animals'] ?? false,

      lipSync:
          json['lip_sync'] ?? true,

      // Accessibility
      subtitles:
          json['subtitles'] ?? true,

      // Thumbnail settings
      autoGenerateThumbnail:
          json[
                  'auto_generate_thumbnail'
              ] ??
              true,

      thumbnailStyle:
          json['thumbnail_style'] ?? '',

      thumbnailTitle:
          json['thumbnail_title'] ?? '',

      thumbnailExpression:
          json[
                  'thumbnail_expression'
              ] ??
              '',

      includeMainCharacter:
          json[
                  'include_main_character'
              ] ??
              true,

      // Approval workflow
      approvalStatus:
          json['approval_status'] ??
              'PENDING_REVIEW',

      approvalReason:
          json['approval_reason'],

      reviewedAt:
          json['reviewed_at'],

      autoApproved:
          json['auto_approved'] ?? false,

      // Scheduling workflow
      scheduleStatus:
          json['schedule_status'] ??
              'NOT_SCHEDULED',

      scheduledAt:
          json['scheduled_at'],

      scheduledPlatform:
          json[
              'scheduled_platform'
          ],

      scheduleTimezone:
          json[
              'schedule_timezone'
          ],

      // Scenes
      scenes:
          (json['scenes']
                      as List<dynamic>? ??
                  [])
              .map(
                (scene) =>
                    Scene.fromJson(
                  scene
                      as Map<
                          String,
                          dynamic>,
                ),
              )
              .toList(),
    );
  }

  // ==========================================================
  // HELPER STATUS GETTERS
  // ==========================================================

  bool get isGenerating {
    final value =
        status.toLowerCase();

    return value == 'queued' ||
        value == 'pending' ||
        value == 'processing' ||
        value == 'generating';
  }

  bool get isCompleted {
    return status.toLowerCase() ==
        'completed';
  }

  bool get isCancelled {
    return status.toLowerCase() ==
        'cancelled';
  }

  bool get hasFailed {
    return status.toLowerCase() ==
        'failed';
  }

  bool get isApproved {
    return approvalStatus ==
        'APPROVED';
  }

  bool get isScheduled {
    return scheduleStatus ==
        'SCHEDULED';
  }

  // ==========================================================
  // DISPLAY TITLE
  // ==========================================================

  String get displayTitle {
    final title =
        thumbnailTitle.trim();

    if (title.isNotEmpty) {
      return title;
    }

    final story =
        prompt.trim();

    if (story.isEmpty) {
      return 'Untitled Aadwik Movie';
    }

    if (story.length <= 42) {
      return story;
    }

    return '${story.substring(0, 42)}...';
  }

  // ==========================================================
  // STORY PREVIEW
  // ==========================================================

  String get storyPreview {
    final story =
        prompt.trim();

    if (story.isEmpty) {
      return 'No story preview available.';
    }

    if (story.length <= 120) {
      return story;
    }

    return '${story.substring(0, 120)}...';
  }
}