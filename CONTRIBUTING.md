# Contributing to Doom-RLVR

Thank you for your interest in contributing to Doom-RLVR! This document provides guidelines for contributing to the project.

## 🎯 How to Contribute

### Reporting Issues

1. **Check existing issues** first to avoid duplicates
2. Use the issue templates when available
3. Include:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Claude Code version
   - Any error messages

### Suggesting Features

1. Open a discussion in the [Discussions](https://github.com/asifnawaz/claude-code-rlvr-spec-system/discussions) tab
2. Describe the use case
3. Explain how it benefits users
4. Consider implementation complexity

### Code Contributions

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. **Test** thoroughly
5. **Commit** with clear messages (`git commit -m 'Add amazing feature'`)
6. **Push** to your fork (`git push origin feature/amazing-feature`)
7. Open a **Pull Request**

## 📋 Development Guidelines

### Code Style

- Python: Follow PEP 8
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused

### Constraints

Remember Doom-RLVR's constraints:
- **No external dependencies** - Python standard library only
- **Claude Code compatible** - Must work within Claude Code environment
- **File-based state** - No persistent processes or databases

### Testing

Before submitting:
1. Test all hooks manually
2. Verify commands work
3. Check agent selection logic
4. Ensure RLVR evaluation runs

### Documentation

- Update README.md if needed
- Add docstrings to new functions
- Update ARCHITECTURE.md for structural changes
- Include examples in docs

## 🚀 Areas for Contribution

### High Priority

1. **New Task Types**
   - Add detection patterns in `UserPromptSubmit`
   - Create optimization templates
   - Design specialized agents

2. **Evaluation Metrics**
   - Enhance RLVR components
   - Add domain-specific metrics
   - Improve feedback generation

3. **Performance Analysis**
   - Better visualization tools
   - Trend analysis
   - Anomaly detection

### Good First Issues

- Improve error messages
- Add more examples to documentation
- Enhance command help text
- Create additional agent templates

### Advanced Features

- Multi-language support
- Custom reward functions
- Advanced learning algorithms
- Cross-project agent sharing

## 🧪 Testing Your Changes

### Manual Testing

```bash
# Test task detection
echo '{"userPrompt":"fix the login bug"}' | python3 .claude/hooks/UserPromptSubmit

# Test evaluation
python3 .claude/scripts/rlvr-evaluate.py test-task agent-test completed

# Test commands
/kiro-status
/kiro-leaderboard
```

### Integration Testing

1. Copy `.claude` to a test project
2. Try various natural language prompts
3. Verify agent selection
4. Check evaluation results

## 📝 Pull Request Process

1. **Title**: Clear and descriptive
2. **Description**: 
   - What changes were made
   - Why they were needed
   - How they were tested
3. **Checklist**:
   - [ ] Code follows style guidelines
   - [ ] No external dependencies added
   - [ ] Documentation updated
   - [ ] All hooks tested
   - [ ] Commands verified

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Public or private harassment
- Publishing private information

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Thanked in the community

## 💬 Getting Help

- Open a discussion for questions
- Join community chat (if available)
- Read existing documentation
- Ask in pull request comments

Thank you for contributing to Doom-RLVR!