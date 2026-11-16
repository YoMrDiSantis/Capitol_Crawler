import { writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { civicsQuestions } from '../src/civics-questions';
import { isCorrectCivicsAnswer } from '../src/civics-validation';
import { displayChoice, questionChoices } from '../src/game';

type OptionReview = {
  choice: string;
  displayedChoice: string;
  acceptedByValidator: boolean;
};

const reviews = civicsQuestions.map((question) => {
  const options: OptionReview[] = question.dynamic
    ? []
    : questionChoices(question, 12).map((choice) => ({
      choice,
      displayedChoice: displayChoice(question, choice),
      acceptedByValidator: isCorrectCivicsAnswer(question, displayChoice(question, choice))
    }));

  return {
    id: question.id,
    prompt: question.prompt,
    category: question.category,
    dynamic: question.dynamic,
    acceptedAnswers: question.acceptedAnswers,
    options,
    validOptionCount: options.filter((option) => option.acceptedByValidator).length,
    duplicateDisplayedOptions: options
      .map((option) => option.displayedChoice)
      .filter((choice, index, allChoices) => allChoices.indexOf(choice) !== index)
  };
});

const report = {
  generatedAt: new Date().toISOString(),
  totalQuestions: reviews.length,
  staticQuestions: reviews.filter((review) => !review.dynamic).length,
  dynamicQuestions: reviews.filter((review) => review.dynamic).map((review) => review.id),
  issues: reviews.filter((review) => !review.dynamic && (review.options.length !== 12 || review.validOptionCount !== 1 || review.duplicateDisplayedOptions.length > 0)),
  questions: reviews
};

const reportPath = join(tmpdir(), 'civics-question-review.json');
writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(`Wrote ${report.totalQuestions}-question review to ${reportPath}`);
console.log(`Static-question issues: ${report.issues.length}`);
for (const issue of report.issues) console.log(`Q${issue.id}: ${issue.options.length} options, ${issue.validOptionCount} valid, duplicates: ${issue.duplicateDisplayedOptions.join(', ') || 'none'}`);
