import 'package:flutter/material.dart';

import '../models/movie.dart';


class SceneBreakdownScreen extends StatelessWidget {
  final List<Scene> scenes;

  const SceneBreakdownScreen({
    super.key,
    required this.scenes,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scene Breakdown'),
      ),
      body: scenes.isEmpty
          ? const Center(
              child: Text(
                'No scenes were generated for this movie.',
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: scenes.length,
              itemBuilder: (context, index) {
                final scene = scenes[index];

                return Card(
                  margin: const EdgeInsets.only(
                    bottom: 16,
                  ),
                  child: ExpansionTile(
                    leading: CircleAvatar(
                      child: Text(
                        scene.sceneNumber.toString(),
                      ),
                    ),

                    title: Row(
                      children: [
                        Expanded(
                          child: Text(
                            scene.title,
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),

                        const SizedBox(width: 8),

                        _buildStatusBadge(
                          scene.status,
                        ),
                      ],
                    ),

                    subtitle: Column(
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 6),

                        Text(
                          '${scene.estimatedDurationSeconds} seconds • ${scene.emotion}',
                        ),

                        const SizedBox(height: 8),

                        LinearProgressIndicator(
                          value:
                              scene.sceneProgress / 100,
                          minHeight: 6,
                        ),

                        const SizedBox(height: 4),

                        Text(
                          '${scene.sceneProgress}% • ${scene.productionStep}',
                          style:
                              Theme.of(context)
                                  .textTheme
                                  .bodySmall,
                        ),
                      ],
                    ),

                    childrenPadding:
                        const EdgeInsets.all(16),

                    children: [
                      _buildProductionSection(
                        scene,
                      ),

                      _buildSection(
                        title: 'Description',
                        content: scene.description,
                      ),

                      _buildSection(
                        title: 'Characters',
                        content:
                            scene.characters.isEmpty
                                ? 'No characters specified'
                                : scene.characters.join(', '),
                      ),

                      _buildSection(
                        title: 'Dialogue',
                        content: scene.dialogue,
                      ),

                      _buildSection(
                        title: 'Emotion',
                        content: scene.emotion,
                      ),

                      _buildSection(
                        title: 'Visual Direction',
                        content:
                            scene.visualDirection,
                      ),

                      _buildSection(
                        title: 'Camera Direction',
                        content:
                            scene.cameraDirection,
                      ),

                      _buildSection(
                        title: 'Music Mood',
                        content: scene.musicMood,
                      ),

                      _buildSection(
                        title: 'Sound Effects',
                        content:
                            scene.soundEffects.isEmpty
                                ? 'No sound effects'
                                : scene.soundEffects.join(', '),
                      ),

                      _buildSection(
                        title: 'Estimated Duration',
                        content:
                            '${scene.estimatedDurationSeconds} seconds',
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }

  Widget _buildProductionSection(
    Scene scene,
  ) {
    return Padding(
      padding: const EdgeInsets.only(
        bottom: 20,
      ),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          borderRadius:
              BorderRadius.circular(12),
          border: Border.all(
            color: _statusColor(
              scene.status,
            ),
          ),
        ),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [
            const Text(
              'Scene Production Status',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                const Text(
                  'Status: ',
                  style: TextStyle(
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),

                _buildStatusBadge(
                  scene.status,
                ),
              ],
            ),

            const SizedBox(height: 12),

            Text(
              scene.productionStep,
            ),

            const SizedBox(height: 12),

            LinearProgressIndicator(
              value:
                  scene.sceneProgress / 100,
              minHeight: 8,
            ),

            const SizedBox(height: 6),

            Text(
              '${scene.sceneProgress}% completed',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(
    String status,
  ) {
    final color = _statusColor(
      status,
    );

    final icon = _statusIcon(
      status,
    );

    return Container(
      padding:
          const EdgeInsets.symmetric(
        horizontal: 8,
        vertical: 4,
      ),
      decoration: BoxDecoration(
        color: color.withValues(
          alpha: 0.15,
        ),
        borderRadius:
            BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize:
            MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 14,
            color: color,
          ),

          const SizedBox(width: 4),

          Text(
            status.replaceAll(
              '_',
              ' ',
            ),
            style: TextStyle(
              fontSize: 11,
              fontWeight:
                  FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Color _statusColor(
    String status,
  ) {
    switch (status) {
      case 'COMPLETED':
        return Colors.green;

      case 'RENDERED':
        return Colors.orange;

      case 'GENERATING':
        return Colors.purple;

      case 'ASSETS_READY':
        return Colors.blue;

      case 'PLANNED':
      default:
        return Colors.amber;
    }
  }

  IconData _statusIcon(
    String status,
  ) {
    switch (status) {
      case 'COMPLETED':
        return Icons.check_circle;

      case 'RENDERED':
        return Icons.movie;

      case 'GENERATING':
        return Icons.auto_awesome;

      case 'ASSETS_READY':
        return Icons.inventory_2;

      case 'PLANNED':
      default:
        return Icons.schedule;
    }
  }

  Widget _buildSection({
    required String title,
    required String content,
  }) {
    return Padding(
      padding: const EdgeInsets.only(
        bottom: 16,
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight:
                  FontWeight.bold,
            ),
          ),

          const SizedBox(height: 6),

          Text(
            content,
          ),
        ],
      ),
    );
  }
}
