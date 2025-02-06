# Installation

Prompter runs on OSX and Linux. You'll find the latest release on the project's [releases page](https://github.com/odewahn/prompter/releases).

## OSX

Download and install the package. Even though this is a Python prject, the release is a compiled binary and will require no other dependencies.

## Linux

You can download the binary and run it directly. Here's how you can do it on Ubuntu:

```
wget https://github.com/odewahn/prompter/releases/download/0.6.1/prompter.ubuntu
mv prompter.ubuntu prompter
chmod +x prompter
```

## Authentication with OpenAI

Prompter requires an API key from OpenAI. You can get one by signing up for an account at [OpenAI](https://beta.openai.com/signup/). Once you have an account, you can find your API key on the [API settings page](https://beta.openai.com/account/api-keys).

Once you have your API key, you can set it as an environment variable like this:

```
export OPENAI_API_KEY=your-api-key
```

Prompter will warn you if you haven't set this variable.
