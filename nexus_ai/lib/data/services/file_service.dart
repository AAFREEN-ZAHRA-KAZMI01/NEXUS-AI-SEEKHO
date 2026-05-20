import 'package:file_picker/file_picker.dart';

class FileService {
  static const Map<String, List<String>> _allowedExtensions = {
    'pdf':   ['pdf'],
    'docx':  ['docx', 'doc'],
    'csv':   ['csv'],
    'excel': ['xlsx', 'xls'],
  };

  static Future<({String name, List<int> bytes, String inputType})?> pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'docx', 'doc', 'csv', 'xlsx', 'xls'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) return null;

    final file = result.files.first;
    if (file.bytes == null) return null;

    final ext = file.extension?.toLowerCase() ?? '';
    final inputType = _allowedExtensions.entries
      .firstWhere(
        (e) => e.value.contains(ext),
        orElse: () => const MapEntry('text', []),
      ).key;

    return (
      name: file.name,
      bytes: file.bytes!.toList(),
      inputType: inputType,
    );
  }

  static String formatFileSize(int bytes) {
    if (bytes < 1024)    return '${bytes}B';
    if (bytes < 1048576) return '${(bytes / 1024).toStringAsFixed(1)}KB';
    return '${(bytes / 1048576).toStringAsFixed(1)}MB';
  }
}
