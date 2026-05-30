import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/constants/app_constants.dart';
import '../../../data/services/api_service.dart';

class OrgSetupScreen extends StatefulWidget {
  const OrgSetupScreen({super.key});

  @override
  State<OrgSetupScreen> createState() => _OrgSetupScreenState();
}

class _OrgSetupScreenState extends State<OrgSetupScreen> {
  final _nameController = TextEditingController();
  final _keyController = TextEditingController();
  bool _isLoading = false;
  Map<String, dynamic>? _orgDetails;

  @override
  void initState() {
    super.initState();
    _checkExistingOrg();
  }

  Future<void> _checkExistingOrg() async {
    final prefs = await SharedPreferences.getInstance();
    final key = prefs.getString(AppConstants.apiKeyPrefKey);
    if (key != null && key.isNotEmpty) {
      _fetchOrgDetails();
    }
  }

  Future<void> _fetchOrgDetails() async {
    setState(() => _isLoading = true);
    try {
      final details = await ApiService().getOrgMe();
      setState(() => _orgDetails = details);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to load org details: $e')));
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _registerOrg() async {
    final name = _nameController.text.trim();
    if (name.isEmpty) return;

    setState(() => _isLoading = true);
    try {
      final res = await ApiService().registerOrg(name);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConstants.apiKeyPrefKey, res['api_key']);
      await prefs.setString(AppConstants.orgIdPrefKey, res['org_id']);
      setState(() => _orgDetails = res);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Organisation created successfully')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to create org: $e')));
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _connectKey() async {
    final key = _keyController.text.trim();
    if (key.isEmpty) return;

    setState(() => _isLoading = true);
    try {
      // Temporarily save key to allow getOrgMe to use it
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConstants.apiKeyPrefKey, key);
      
      final res = await ApiService().getOrgMe();
      await prefs.setString(AppConstants.orgIdPrefKey, res['org_id']);
      
      setState(() => _orgDetails = res);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Connected successfully')));
      }
    } catch (e) {
      // Revert if failed
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(AppConstants.apiKeyPrefKey);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Invalid API key: $e')));
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }
  
  Future<void> _disconnect() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.apiKeyPrefKey);
    await prefs.remove(AppConstants.orgIdPrefKey);
    setState(() {
      _orgDetails = null;
      _nameController.clear();
      _keyController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Organisation Setup')),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator())
        : Padding(
            padding: const EdgeInsets.all(16.0),
            child: _orgDetails != null ? _buildOrgDetails() : _buildSetupForms(),
          ),
    );
  }

  Widget _buildSetupForms() {
    return ListView(
      children: [
        const Text('Create New Organisation', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        TextField(
          controller: _nameController,
          decoration: const InputDecoration(labelText: 'Organisation Name', border: OutlineInputBorder()),
        ),
        const SizedBox(height: 16),
        ElevatedButton(
          onPressed: _registerOrg,
          child: const Text('Register'),
        ),
        const SizedBox(height: 32),
        const Divider(),
        const SizedBox(height: 32),
        const Text('I have an API key', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        TextField(
          controller: _keyController,
          decoration: const InputDecoration(labelText: 'API Key', border: OutlineInputBorder()),
        ),
        const SizedBox(height: 16),
        ElevatedButton(
          onPressed: _connectKey,
          child: const Text('Connect'),
        ),
      ],
    );
  }

  Widget _buildOrgDetails() {
    final name = _orgDetails?['name'] ?? 'Unknown';
    final plan = _orgDetails?['plan'] ?? 'free';
    final used = _orgDetails?['monthly_analysis_count'] ?? 0;
    final limit = _orgDetails?['monthly_limit'] ?? 50;
    final progress = limit > 0 ? (used / limit).clamp(0.0, 1.0) : 0.0;
    final apiKey = _orgDetails?['api_key']; // only returned on register

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Organisation: $name', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        Chip(label: Text('Plan: $plan')),
        const SizedBox(height: 24),
        const Text('Monthly Usage', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        LinearProgressIndicator(value: progress),
        const SizedBox(height: 8),
        Text('$used of $limit analyses used this month'),
        if (apiKey != null) ...[
          const SizedBox(height: 24),
          const Text('Your API Key (Save this!)', style: TextStyle(fontWeight: FontWeight.bold)),
          SelectableText(apiKey),
        ],
        const Spacer(),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton(
            onPressed: _disconnect,
            child: const Text('Disconnect'),
          ),
        )
      ],
    );
  }
}
