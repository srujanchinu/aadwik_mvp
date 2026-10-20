import 'package:flutter/material.dart';

import '../models/movie.dart';
import '../services/movie_service.dart';

class ScheduleMovieScreen extends StatefulWidget {
  final Movie movie;

  const ScheduleMovieScreen({
    super.key,
    required this.movie,
  });

  @override
  State<ScheduleMovieScreen> createState() =>
      _ScheduleMovieScreenState();
}

class _ScheduleMovieScreenState
    extends State<ScheduleMovieScreen> {
  final MovieService service = MovieService();

  DateTime? selectedDateTime;

  String selectedPlatform = 'YouTube';

  String selectedTimezone =
      'Asia/Kolkata';

  bool saving = false;

  final List<String> platforms = [
    'YouTube',
    'Instagram',
    'Facebook',
  ];

  final List<String> timezones = [
    'Asia/Kolkata',
    'UTC',
    'America/New_York',
    'Europe/London',
  ];

  Future<void> selectDate() async {
    final now = DateTime.now();

    final pickedDate =
        await showDatePicker(
      context: context,
      initialDate:
          selectedDateTime ?? now,
      firstDate: now,
      lastDate:
          DateTime(now.year + 5),
    );

    if (pickedDate == null) {
      return;
    }

    if (!mounted) return;

    final pickedTime =
        await showTimePicker(
      context: context,
      initialTime:
          selectedDateTime != null
              ? TimeOfDay.fromDateTime(
                  selectedDateTime!,
                )
              : TimeOfDay.now(),
    );

    if (pickedTime == null) {
      return;
    }

    setState(() {
      selectedDateTime = DateTime(
        pickedDate.year,
        pickedDate.month,
        pickedDate.day,
        pickedTime.hour,
        pickedTime.minute,
      );
    });
  }

  Future<void> saveSchedule() async {
    if (selectedDateTime == null) {
      ScaffoldMessenger.of(context)
          .showSnackBar(
        const SnackBar(
          content: Text(
            'Please select a date and time first.',
          ),
        ),
      );
      return;
    }

    setState(() {
      saving = true;
    });

    try {
      await service.scheduleMovie(
        movieId: widget.movie.movieId,
        scheduledAt:
            selectedDateTime!
                .toIso8601String(),
        platform: selectedPlatform,
        timezone: selectedTimezone,
      );

      if (!mounted) return;

      setState(() {
        saving = false;
      });

      ScaffoldMessenger.of(context)
          .showSnackBar(
        SnackBar(
          content: Text(
            'Movie scheduled successfully for '
            '${selectedDateTime!.day}/'
            '${selectedDateTime!.month}/'
            '${selectedDateTime!.year} '
            'at '
            '${TimeOfDay.fromDateTime(selectedDateTime!).format(context)} '
            'on $selectedPlatform 📅',
          ),
        ),
      );

      // IMPORTANT:
      // GenerationScreen opens this route as Navigator.push<bool>.
      // Therefore this route must return a bool, not a Movie.
      Navigator.pop<bool>(
        context,
        true,
      );
    } catch (e) {
      if (!mounted) return;

      setState(() {
        saving = false;
      });

      ScaffoldMessenger.of(context)
          .showSnackBar(
        SnackBar(
          content: Text(
            'Could not save schedule: $e',
          ),
        ),
      );
    }
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Schedule Movie',
        ),
      ),
      body: SingleChildScrollView(
        padding:
            const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding:
                    const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(
                          Icons.movie,
                        ),
                        SizedBox(
                          width: 10,
                        ),
                        Text(
                          'Movie Ready for Schedule',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight:
                                FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(
                      height: 16,
                    ),
                    Text(
                      widget.movie.prompt.isEmpty
                          ? 'Aadwik Movie'
                          : widget.movie.prompt,
                      maxLines: 4,
                      overflow:
                          TextOverflow.ellipsis,
                    ),
                    const SizedBox(
                      height: 12,
                    ),
                    Text(
                      'Movie ID: '
                      '${widget.movie.movieId}',
                      style:
                          Theme.of(context)
                              .textTheme
                              .bodySmall,
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(
              height: 24,
            ),

            const Text(
              'Publishing Platform',
              style: TextStyle(
                fontSize: 18,
                fontWeight:
                    FontWeight.bold,
              ),
            ),

            const SizedBox(
              height: 10,
            ),

            DropdownButtonFormField<String>(
              initialValue:
                  selectedPlatform,
              decoration:
                  const InputDecoration(
                border:
                    OutlineInputBorder(),
                labelText:
                    'Platform',
                prefixIcon:
                    Icon(Icons.public),
              ),
              items: platforms
                  .map(
                    (platform) =>
                        DropdownMenuItem<String>(
                      value:
                          platform,
                      child:
                          Text(platform),
                    ),
                  )
                  .toList(),
              onChanged: saving
                  ? null
                  : (value) {
                      if (value == null) {
                        return;
                      }

                      setState(() {
                        selectedPlatform =
                            value;
                      });
                    },
            ),

            const SizedBox(
              height: 24,
            ),

            const Text(
              'Timezone',
              style: TextStyle(
                fontSize: 18,
                fontWeight:
                    FontWeight.bold,
              ),
            ),

            const SizedBox(
              height: 10,
            ),

            DropdownButtonFormField<String>(
              initialValue:
                  selectedTimezone,
              decoration:
                  const InputDecoration(
                border:
                    OutlineInputBorder(),
                labelText:
                    'Timezone',
                prefixIcon:
                    Icon(Icons.language),
              ),
              items: timezones
                  .map(
                    (timezone) =>
                        DropdownMenuItem<String>(
                      value:
                          timezone,
                      child:
                          Text(timezone),
                    ),
                  )
                  .toList(),
              onChanged: saving
                  ? null
                  : (value) {
                      if (value == null) {
                        return;
                      }

                      setState(() {
                        selectedTimezone =
                            value;
                      });
                    },
            ),

            const SizedBox(
              height: 24,
            ),

            const Text(
              'Schedule Date & Time',
              style: TextStyle(
                fontSize: 18,
                fontWeight:
                    FontWeight.bold,
              ),
            ),

            const SizedBox(
              height: 10,
            ),

            OutlinedButton.icon(
              onPressed: saving
                  ? null
                  : selectDate,
              icon: const Icon(
                Icons.calendar_month,
              ),
              label: Text(
                selectedDateTime == null
                    ? 'SELECT DATE & TIME'
                    : '${selectedDateTime!.day}/'
                        '${selectedDateTime!.month}/'
                        '${selectedDateTime!.year}  '
                        '${TimeOfDay.fromDateTime(selectedDateTime!).format(context)}',
              ),
            ),

            const SizedBox(
              height: 10,
            ),

            Text(
              'Timezone: '
              '$selectedTimezone',
              textAlign:
                  TextAlign.center,
              style:
                  Theme.of(context)
                      .textTheme
                      .bodySmall,
            ),

            const SizedBox(
              height: 32,
            ),

            FilledButton.icon(
              onPressed: saving
                  ? null
                  : saveSchedule,
              icon: saving
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child:
                          CircularProgressIndicator(
                        strokeWidth: 2,
                      ),
                    )
                  : const Icon(
                      Icons.schedule_send,
                    ),
              label: Text(
                saving
                    ? 'SAVING...'
                    : 'SAVE SCHEDULE',
              ),
              style:
                  FilledButton.styleFrom(
                padding:
                    const EdgeInsets.all(
                  16,
                ),
              ),
            ),

            const SizedBox(
              height: 16,
            ),

            const Text(
              'Only approved movies should enter '
              'the publishing schedule.',
              textAlign:
                  TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
