import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/constants/app_constants.dart';
import '../../../data/services/api_service.dart';

class CreateAlertScreen extends StatefulWidget {
  const CreateAlertScreen({super.key});

  @override
  State<CreateAlertScreen> createState() => _CreateAlertScreenState();
}

class _CreateAlertScreenState extends State<CreateAlertScreen> {
  final _formKey = GlobalKey<FormState>();
  final ApiService _apiService = ApiService();

  String _selectedDomain = 'finance';
  String _selectedConditionType = 'severity_above'; // severity_above, kpi_change, domain_keyword

  final TextEditingController _valueController = TextEditingController();
  final TextEditingController _labelController = TextEditingController();
  
  bool _isSubmitting = false;

  @override
  void dispose() {
    _valueController.dispose();
    _labelController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);

    try {
      final value = _valueController.text.trim();
      final label = _labelController.text.trim();

      // For domain_keyword, we set keyword to the same string
      final isKeyword = _selectedConditionType == 'domain_keyword';

      final payload = {
        'domain': _selectedDomain,
        'condition_type': _selectedConditionType,
        'condition_value': value,
        'keyword': isKeyword ? value : null,
        'label': label,
        'user_id': AppConstants.deviceId,
      };

      await _apiService.createAlert(payload);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Watchlist Alert "$label" Created Successfully!', style: AppTextStyles.bodyMedium.copyWith(color: Colors.black)),
            backgroundColor: primaryColor,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to create alert: $e', style: AppTextStyles.bodyMedium),
            backgroundColor: errorColor,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final valueLabel = _selectedConditionType == 'domain_keyword'
        ? 'Keyword Phrase'
        : _selectedConditionType == 'severity_above'
            ? 'Severity Threshold (1-10)'
            : 'KPI Threshold Percentage (%)';

    final valueHint = _selectedConditionType == 'domain_keyword'
        ? 'e.g., strike, outage, surge, depreciation'
        : _selectedConditionType == 'severity_above'
            ? 'e.g., 7'
            : 'e.g., 15';

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: surfaceColor,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: textColor),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('Create Watchlist Alert', style: AppTextStyles.heading2),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Domain Watchlist', style: AppTextStyles.heading3),
              const SizedBox(height: 8),
              Text(
                'Select which operational domain this alert will monitor.',
                style: AppTextStyles.bodySmall,
              ),
              const SizedBox(height: 12),
              
              // Dropdown
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: cardColor,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: borderColor, width: 1.5),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: _selectedDomain,
                    dropdownColor: cardColor,
                    isExpanded: true,
                    icon: const Icon(Icons.keyboard_arrow_down, color: primaryColor),
                    items: AppConstants.domains.map((String domain) {
                      return DropdownMenuItem<String>(
                        value: domain,
                        child: Row(
                          children: [
                            Text(
                              AppConstants.domainIcons[domain.toLowerCase()] ?? '🔔',
                              style: const TextStyle(fontSize: 16),
                            ),
                            const SizedBox(width: 12),
                            Text(
                              AppConstants.domainLabels[domain] ?? domain.toUpperCase(),
                              style: AppTextStyles.bodyMedium.copyWith(color: textColor),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) {
                        setState(() {
                          _selectedDomain = val;
                        });
                      }
                    },
                  ),
                ),
              ),
              
              const SizedBox(height: 28),
              Text('Condition Type', style: AppTextStyles.heading3),
              const SizedBox(height: 12),

              // Severity above option
              _buildConditionRadio(
                type: 'severity_above',
                title: 'Severity Exceeds Threshold',
                desc: 'Triggers when domain severity exceeds a specified index (e.g. trigger if severity > 7).',
                icon: Icons.warning_amber_rounded,
              ),
              const SizedBox(height: 12),

              // KPI change option
              _buildConditionRadio(
                type: 'kpi_change',
                title: 'KPI Change Rate Exceeds',
                desc: 'Triggers when absolute percent delta of any domain KPI exceeds threshold (e.g. trigger if KPI change > 15%).',
                icon: Icons.trending_up_rounded,
              ),
              const SizedBox(height: 12),

              // Domain keyword option
              _buildConditionRadio(
                type: 'domain_keyword',
                title: 'Keyword Match',
                desc: 'Triggers when a specific key phrase is extracted in the session brief insight.',
                icon: Icons.key_rounded,
              ),

              const SizedBox(height: 28),
              Text('Trigger Parameters', style: AppTextStyles.heading3),
              const SizedBox(height: 16),

              // Value input
              TextFormField(
                controller: _valueController,
                keyboardType: _selectedConditionType == 'domain_keyword'
                    ? TextInputType.text
                    : TextInputType.number,
                style: AppTextStyles.body,
                decoration: InputDecoration(
                  labelText: valueLabel,
                  labelStyle: AppTextStyles.bodySmall.copyWith(color: primaryColor),
                  hintText: valueHint,
                  hintStyle: AppTextStyles.bodySmall.copyWith(color: text4Color),
                  fillColor: cardColor,
                  filled: true,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: borderColor),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: primaryColor, width: 2),
                  ),
                ),
                validator: (val) {
                  if (val == null || val.trim().isEmpty) {
                    return 'Please enter a threshold/keyword value';
                  }
                  if (_selectedConditionType == 'severity_above') {
                    final numVal = int.tryParse(val.trim());
                    if (numVal == null || numVal < 1 || numVal > 10) {
                      return 'Enter an integer between 1 and 10';
                    }
                  } else if (_selectedConditionType == 'kpi_change') {
                    final numVal = double.tryParse(val.trim());
                    if (numVal == null || numVal <= 0) {
                      return 'Enter a positive numeric percentage';
                    }
                  }
                  return null;
                },
              ),

              const SizedBox(height: 20),

              // Label Input
              TextFormField(
                controller: _labelController,
                textCapitalization: TextCapitalization.words,
                style: AppTextStyles.body,
                decoration: InputDecoration(
                  labelText: 'Alert Label (Custom Name)',
                  labelStyle: AppTextStyles.bodySmall.copyWith(color: primaryColor),
                  hintText: 'e.g., Critical Gas Shortage / Finance FX Volatility',
                  hintStyle: AppTextStyles.bodySmall.copyWith(color: text4Color),
                  fillColor: cardColor,
                  filled: true,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: borderColor),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: primaryColor, width: 2),
                  ),
                ),
                validator: (val) {
                  if (val == null || val.trim().isEmpty) {
                    return 'Please provide a unique, descriptive label';
                  }
                  return null;
                },
              ),

              const SizedBox(height: 36),

              // Create Button
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: _isSubmitting ? null : _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    padding: EdgeInsets.zero,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Ink(
                    decoration: BoxDecoration(
                      gradient: primaryGrad,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Container(
                      alignment: Alignment.center,
                      child: _isSubmitting
                          ? const CircularProgressIndicator(color: Colors.black)
                          : Text(
                              'CREATE WATCHLIST ALERT',
                              style: AppTextStyles.buttonLabel.copyWith(color: Colors.black),
                            ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildConditionRadio({
    required String type,
    required String title,
    required String desc,
    required IconData icon,
  }) {
    final isSelected = _selectedConditionType == type;

    return InkWell(
      onTap: () {
        setState(() {
          _selectedConditionType = type;
          _valueController.clear();
        });
      },
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isSelected ? primaryColor.withOpacity(0.05) : cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? primaryColor : borderColor,
            width: isSelected ? 1.8 : 1.5,
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: isSelected ? primaryColor.withOpacity(0.15) : borderColor,
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: isSelected ? primaryColor : text3Color, size: 20),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: AppTextStyles.heading4.copyWith(
                      color: isSelected ? primaryColor : textColor,
                      fontWeight: isSelected ? FontWeight.bold : null,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    desc,
                    style: AppTextStyles.bodySmall.copyWith(color: isSelected ? text2Color : text3Color),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            Container(
              width: 18,
              height: 18,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: isSelected ? primaryColor : text3Color,
                  width: 2,
                ),
              ),
              child: isSelected
                  ? Center(
                      child: Container(
                        width: 10,
                        height: 10,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          color: primaryColor,
                        ),
                      ),
                    )
                  : null,
            )
          ],
        ),
      ),
    );
  }
}
