import 'package:flutter/material.dart';
import '../services/movie_service.dart';
import 'generation_screen.dart';

class CreateMovieScreen extends StatefulWidget {
  const CreateMovieScreen({super.key});

  @override
  State<CreateMovieScreen> createState() => _CreateMovieScreenState();
}

class _CreateMovieScreenState extends State<CreateMovieScreen> {
  final story = TextEditingController();
  final thumbnailTitle = TextEditingController();
  final service = MovieService();

  String style = 'Auto Smart Style';
  String language = 'Auto';
  String genre = 'Fantasy';
  String ageGroup = 'Family / All Ages';
  String characterType = 'Auto Select';
  String musicMood = 'Auto Select';

  String platform = 'YouTube Video';

  String thumbnailStyle = 'Auto Select';
  String thumbnailExpression = 'Excited / Attractive';

  int duration = 5;

  bool talkingAnimals = false;
  bool lipSync = true;
  bool sceneBasedMusic = true;
  bool soundEffects = true;
  bool subtitles = true;

  bool autoGenerateThumbnail = true;
  bool includeMainCharacter = true;

  bool loading = false;
  bool autoStoryLoading = false;

Future<void> generateAutoStory() async {
  if (autoStoryLoading || loading) return;

  setState(() => autoStoryLoading = true);

  try {
    final result = await service.autoStory(
      niche: 'Auto',
      language: 'Auto',
      ageGroup: 'Auto',
    );

    if (!mounted) return;

    final recommendedStyle =
        result['recommended_style']?.toString() ?? 'Auto Smart Style';

    final returnedGenre =
        result['genre']?.toString() ?? 'Fantasy';

    final returnedAgeGroup =
        result['age_group']?.toString() ?? 'Family / All Ages';

    final returnedCharacterType =
        result['character_type']?.toString() ?? 'Auto Select';

    final returnedMusicMood =
        result['music_mood']?.toString() ?? 'Auto Select';

    setState(() {
      story.text = result['story']?.toString() ?? '';

      style = [
        'Auto Smart Style',
        '3D Animation',
        'Cartoon',
        'Anime',
        'Cinematic Animation',
      ].contains(recommendedStyle)
          ? recommendedStyle
          : 'Auto Smart Style';

      genre = [
        'Fantasy',
        'Adventure',
        'Science Fiction',
        'Comedy',
        'Moral Story',
        'Family Story',
        'Mystery',
        'Historical',
        'Mythological',
        'Educational',
      ].contains(returnedGenre)
          ? returnedGenre
          : 'Fantasy';

      ageGroup = returnedAgeGroup == 'All Ages'
          ? 'Family / All Ages'
          : returnedAgeGroup;

      characterType = returnedCharacterType == 'Human'
          ? 'Humans Only'
          : returnedCharacterType == 'Animal'
              ? 'Animals Only'
              : returnedCharacterType == 'Mixed'
                  ? 'Humans + Animals'
                  : 'Auto Select';

      musicMood = [
        'Auto Select',
        'Happy / Fun',
        'Sentimental / Emotional',
        'Sad Scene',
        'Adventure',
        'Fantasy / Magical',
        'Comedy',
        'Mystery',
        'Sci-Fi / Futuristic',
        'Educational / Learning',
        'Kids / Playful',
        'Calm / Relaxing',
        'No Music',
      ].contains(returnedMusicMood)
          ? returnedMusicMood
          : 'Auto Select';

      talkingAnimals = result['talking_animals'] == true;

      language = 'Auto';
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '${result['title'] ?? 'Auto Story'} generated successfully!',
        ),
      ),
    );
  } catch (e) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Could not generate automatic story: $e',
          ),
        ),
      );
    }
  } finally {
    if (mounted) {
      setState(() => autoStoryLoading = false);
    }
  }
}

  Future<void> submit() async {
    final prompt = story.text.trim();

    if (prompt.length < 5) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter a longer story.'),
        ),
      );
      return;
    }

    setState(() => loading = true);

    try {
      final movie = await service.createMovie(
        prompt: prompt,
        style: style,
        language: language,
        durationMinutes: duration,
        genre: genre,
        ageGroup: ageGroup,
        characterType: characterType,
        musicMood: musicMood,
        platform: platform,
        talkingAnimals: talkingAnimals,
        lipSync: lipSync,
        sceneBasedMusic: sceneBasedMusic,
        soundEffects: soundEffects,
        subtitles: subtitles,
        autoGenerateThumbnail: autoGenerateThumbnail,
        thumbnailStyle: thumbnailStyle,
        thumbnailTitle: thumbnailTitle.text.trim(),
        thumbnailExpression: thumbnailExpression,
        includeMainCharacter: includeMainCharacter,
      );


      if (!mounted) return;

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => GenerationScreen(
            movieId: movie.movieId,
          ),
        ),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Could not start generation: $e',
            ),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  String get aspectRatio {
    switch (platform) {
      case 'YouTube Shorts':
      case 'Instagram Reel':
      case 'Facebook Reel':
        return '9:16';

      case 'Instagram Feed Portrait':
        return '4:5';

      case 'Instagram Feed Square':
        return '1:1';

      case 'YouTube Video':
      case 'Facebook Video':
      default:
        return '16:9';
    }
  }

  String get thumbnailRatio {
    switch (platform) {
      case 'Instagram Feed Portrait':
        return '4:5';

      case 'Instagram Feed Square':
        return '1:1';

      case 'YouTube Shorts':
      case 'Instagram Reel':
      case 'Facebook Reel':
        return '9:16';

      default:
        return '16:9';
    }
  }

  Widget sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(
        top: 18,
        bottom: 8,
      ),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget dropdown(
    String label,
    String value,
    List<String> options,
    ValueChanged<String?> onChanged,
  ) {
    return DropdownButtonFormField<String>(
      initialValue: value,
      decoration: InputDecoration(
        border: const OutlineInputBorder(),
        labelText: label,
      ),
      items: options
          .map(
            (item) => DropdownMenuItem(
              value: item,
              child: Text(item),
            ),
          )
          .toList(),
      onChanged: onChanged,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Create Aadwik Movie'),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            const Text(
              'Tell Aadwik your story',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 12),

OutlinedButton.icon(
  onPressed: autoStoryLoading ? null : generateAutoStory,
  icon: autoStoryLoading
      ? const SizedBox(
          height: 18,
          width: 18,
          child: CircularProgressIndicator(strokeWidth: 2),
        )
      : const Icon(Icons.auto_awesome),
  label: Text(
    autoStoryLoading
        ? 'AADWIK IS CREATING A STORY...'
        : 'GENERATE STORY AUTOMATICALLY',
  ),
),

const SizedBox(height: 12),

            TextField(
              controller: story,
              maxLines: 8,
              maxLength: 20000,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'Your story',
                hintText:
                    'A young child and a friendly rabbit discover a magical forest...',
              ),
            ),

            sectionTitle('Genre'),

            dropdown(
              'Genre',
              genre,
              [
                'Fantasy',
                'Adventure',
                'Science Fiction',
                'Comedy',
                'Moral Story',
                'Family Story',
                'Mystery',
                'Historical',
                'Mythological',
                'Educational',
                'Rhymes & Songs',
                'Alphabet Learning',
                'Maths Learning',
                'Exercise & Activity',
              ],
              (v) => setState(() => genre = v!),
            ),

            sectionTitle('Target Audience'),

            dropdown(
              'Age Group',
              ageGroup,
              [
                '1-5 Years',
                '6-10 Years',
                '11-15 Years',
                '16-25 Years',
                '26-40 Years',
                '41-60 Years',
                '60+ Years',
                'Family / All Ages',
              ],
              (v) => setState(() => ageGroup = v!),
            ),

            sectionTitle('Characters'),

            dropdown(
              'Character Type',
              characterType,
              [
                'Auto Select',
                'Humans Only',
                'Animals Only',
                'Humans + Animals',
                'Friendly Robots',
                'Fantasy Creatures',
              ],
              (v) => setState(() => characterType = v!),
            ),

            SwitchListTile(
              title: const Text('Talking Animals'),
              subtitle: const Text(
                'Animals can speak and interact with characters',
              ),
              value: talkingAnimals,
              onChanged: (v) {
                setState(() => talkingAnimals = v);
              },
            ),

            SwitchListTile(
              title: const Text('Lip Sync'),
              subtitle: const Text(
                'Match mouth movement with dialogue',
              ),
              value: lipSync,
              onChanged: (v) {
                setState(() => lipSync = v);
              },
            ),

            sectionTitle('Visual Style'),

            dropdown(
              'Style',
              style,
              [
                'Auto Smart Style',
                '3D Animation',
                'Cartoon',
                'Anime',
                'Cinematic Animation',
              ],
              (v) => setState(() => style = v!),
            ),

            sectionTitle('Language'),

            dropdown(
              'Language',
              language,
              [
  'Auto',
  'English',
  'Hindi',
  'Telugu',
  'Tamil',
  'Kannada',
  'Malayalam',
  'Bengali',
  'Marathi',
  'Gujarati',
  'Punjabi',
  'Urdu',
  'Spanish',
  'French',
  'German',
  'Portuguese',
  'Italian',
  'Russian',
  'Arabic',
  'Chinese',
  'Japanese',
  'Korean',
  'Indonesian',
  'Turkish',
  'Dutch',
  'Polish',
  'Vietnamese',
  'Thai',
  'Swedish',
  'Greek',
],
            
              (v) => setState(() => language = v!),
            ),

            sectionTitle('Music & Sound'),

            dropdown(
              'Music Mood',
              musicMood,
              [
                'Auto Select',
                'Happy / Fun',
                'Sentimental / Emotional',
                'Sad Scene',
                'Adventure',
                'Fantasy / Magical',
                'Comedy',
                'Mystery',
                'Sci-Fi / Futuristic',
                'Educational / Learning',
                'Kids / Playful',
                'Calm / Relaxing',
                'No Music',
              ],
              (v) => setState(() => musicMood = v!),
            ),

            SwitchListTile(
              title: const Text('Scene-Based Music'),
              subtitle: const Text(
                'Automatically change music based on scene emotion',
              ),
              value: sceneBasedMusic,
              onChanged: (v) {
                setState(() => sceneBasedMusic = v);
              },
            ),

            SwitchListTile(
              title: const Text('Sound Effects'),
              subtitle: const Text(
                'Add suitable sounds for scenes and actions',
              ),
              value: soundEffects,
              onChanged: (v) {
                setState(() => soundEffects = v);
              },
            ),

            SwitchListTile(
              title: const Text('Subtitles'),
              subtitle: const Text(
                'Generate subtitles for the selected language',
              ),
              value: subtitles,
              onChanged: (v) {
                setState(() => subtitles = v);
              },
            ),

            sectionTitle('Platform Format'),

            dropdown(
              'Platform',
              platform,
              [
                'YouTube Video',
                'YouTube Shorts',
                'Instagram Reel',
                'Instagram Feed Portrait',
                'Instagram Feed Square',
                'Facebook Video',
                'Facebook Reel',
              ],
              (v) => setState(() => platform = v!),
            ),

            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                'Video Aspect Ratio: $aspectRatio',
              ),
            ),

            sectionTitle('Thumbnail'),

            SwitchListTile(
              title: const Text('Generate Thumbnail Automatically'),
              subtitle: const Text(
                'Create an attractive thumbnail based on the story',
              ),
              value: autoGenerateThumbnail,
              onChanged: (v) {
                setState(() => autoGenerateThumbnail = v);
              },
            ),

            if (autoGenerateThumbnail) ...[
              dropdown(
                'Thumbnail Style',
                thumbnailStyle,
                [
                  'Auto Select',
                  'Cinematic',
                  '3D Animation',
                  'Cartoon',
                  'Colorful Kids',
                  'Fantasy / Magical',
                  'Adventure',
                  'Educational',
                  'Minimal Professional',
                  'Bright Social Media',
                ],
                (v) => setState(() => thumbnailStyle = v!),
              ),

              const SizedBox(height: 16),

              TextField(
                controller: thumbnailTitle,
                maxLength: 100,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  labelText: 'Thumbnail Title / Text',
                  hintText:
                      'Leave empty to let Aadwik create an attractive title',
                ),
              ),

              const SizedBox(height: 16),

              dropdown(
                'Thumbnail Expression',
                thumbnailExpression,
                [
                  'Excited / Attractive',
                  'Happy',
                  'Surprised',
                  'Curious',
                  'Emotional',
                  'Funny',
                  'Adventure / Brave',
                  'Magical / Wonder',
                  'Auto Select',
                ],
                (v) => setState(() => thumbnailExpression = v!),
              ),

              SwitchListTile(
                title: const Text('Include Main Character'),
                subtitle: const Text(
                  'Feature the main character prominently in the thumbnail',
                ),
                value: includeMainCharacter,
                onChanged: (v) {
                  setState(() => includeMainCharacter = v);
                },
              ),

              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  'Thumbnail Format: $thumbnailRatio',
                ),
              ),
            ],

            sectionTitle('Duration'),

            Text(
              'Duration: $duration minutes',
              style: const TextStyle(
                fontSize: 16,
              ),
            ),

            Slider(
              value: duration.toDouble(),
              min: 1,
              max: 30,
              divisions: 29,
              label: '$duration min',
              onChanged: (v) {
                setState(() => duration = v.round());
              },
            ),

            const SizedBox(height: 20),

            FilledButton(
              onPressed: loading ? null : submit,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: loading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                        ),
                      )
                    : const Text(
                        'GENERATE MOVIE',
                      ),
              ),
            ),

            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    story.dispose();
    thumbnailTitle.dispose();
    super.dispose();
  }
}